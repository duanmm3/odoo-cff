"""
Integration of existing Price API code into Odoo
This module adapts the existing price_main.py and supplier_apis.py code
to work within the Odoo framework.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PriceAPIIntegration(models.Model):
    _name = 'price.api.integration'
    _description = 'Price API Integration'
    
    @staticmethod
    def _get_exchange_rates():
        """Get exchange rates"""
        try:
            import requests
            resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
            data = resp.json()
            if data.get("result") == "success":
                rates = data.get("rates", {})
                return {k.upper(): float(v) for k, v in rates.items() if isinstance(v, (int, float))}
        except Exception as e:
            _logger.warning(f"Failed to fetch exchange rates: {e}")
        return {"USD": 1.0, "CNY": 7.2, "EUR": 0.85}
    
    @staticmethod
    def _convert_to_rmb(price: float, currency: str, rates: Dict) -> float:
        """Convert price to RMB"""
        if not currency or not price:
            return 0.0
        cur = currency.upper()
        cur_map = {"RMB": "CNY", "￥": "CNY", "¥": "CNY"}
        cur = cur_map.get(cur, cur)
        
        if cur not in rates:
            return price
        
        usd_rate = rates.get(cur, 1.0)
        cny_rate = rates.get("CNY", 7.2)
        usd_amount = price / usd_rate
        return round(usd_amount * cny_rate, 4)
    
    @staticmethod
    def _convert_to_rmb_static(price: float, currency: str, rates: Dict) -> float:
        """Convert price to RMB (static version)"""
        return PriceAPIIntegration._convert_to_rmb(price, currency, rates)
    
    @staticmethod
    def _query_mouser_api(ic_model: str, api_key: str) -> List[Dict]:
        """Query Mouser API"""
        quotes = []
        try:
            import requests
            import re
            
            url = "https://api.mouser.com/api/v1/search/keyword"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            data = {
                "SearchByKeywordRequest": {
                    "keyword": ic_model,
                    "records": 10,
                    "options": "Details"
                }
            }
            
            response = requests.post(url, json=data, headers=headers, params={"apiKey": api_key}, timeout=15)
            _logger.info(f"Mouser API response: {response.status_code}, text: {response.text[:400] if response.text else 'empty'}")
            _logger.info(f"Mouser request url: {response.url}")
            
            if response.status_code == 200:
                result = response.json()
                parts = result.get("SearchResults", {}).get("Parts", [])
                
                for part in parts:
                    price_breaks = part.get("PriceBreaks", [])
                    price = ""
                    currency = "USD"
                    
                    if price_breaks:
                        price_raw = price_breaks[0].get("Price", "")
                        # 更健壮的价格提取逻辑
                        if price_raw:
                            # 尝试提取数字部分
                            price_match = re.search(r'[\d,.]+', price_raw)
                            if price_match:
                                price_str = price_match.group()
                                # 移除逗号并转换为浮点数
                                price_str = price_str.replace(',', '')
                                try:
                                    price = float(price_str)
                                except:
                                    price = 0.0
                            
                            # 确定货币
                            currency_raw = price_breaks[0].get("Currency", "USD")
                            # 更全面的货币映射
                            currency_map = {
                                "RMB": "CNY", "¥": "CNY", "￥": "CNY",
                                "$": "USD", "US$": "USD",
                                "€": "EUR", "EUR": "EUR",
                                "£": "GBP", "GBP": "GBP",
                                "JPY": "JPY", "¥": "JPY",
                                "KRW": "KRW", "₩": "KRW"
                            }
                            currency = currency_map.get(currency_raw.upper(), "USD")
                    
                    # 处理库存信息
                    availability = part.get("Availability", "")
                    stock_match = re.search(r'(\d+)', str(availability))
                    stock_qty = stock_match.group(1) if stock_match else "0"
                    
                    # 获取最小订购量
                    min_qty = str(part.get("Min", "1"))
                    
                    # 获取零件号
                    part_number = part.get("MouserPartNumber", ic_model)
                    
                    # 构建链接
                    link = f"https://www.mouser.com/ProductDetail/{part_number}" if part_number else ""
                    
                    quotes.append({
                        "supplier": "Mouser",
                        "part_number": part_number,
                        "manufacturer": part.get("Manufacturer", ""),
                        "price": str(price) if price else "",
                        "currency": currency,
                        "stock": stock_qty,
                        "moq": min_qty,
                        "lead_time": part.get("LeadTime", ""),
                        "link": link,
                        "source": "Mouser API",
                        "rmb": 0.0,
                    })
                    
                _logger.info(f"Mouser API 返回 {len(quotes)} 个报价")
                
            elif response.status_code != 200:
                _logger.warning(f"Mouser API error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            _logger.warning(f"Mouser API query failed: {e}")
            import traceback
            traceback.print_exc()
            
        return quotes
    
    @staticmethod
    def _query_oemsecrets_api(ic_model: str, api_key: str) -> List[Dict]:
        """Query OEMSecrets API"""
        quotes = []
        try:
            import requests
            import re
            
            url = "https://beta.api.oemsecrets.com/partsearch"
            params = {
                "searchTerm": ic_model,
                "apiKey": api_key,
            }
            
            response = requests.get(url, params=params, timeout=15)
            _logger.info(f"OEMSecrets API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                stock_items = result.get("stock", [])
                
                _logger.info(f"OEMSecrets API 返回 {len(stock_items)} 个库存项目")
                
                for item in stock_items[:15]:  # 最多取15个
                    # 获取分销商信息
                    distributor = item.get("distributor", {})
                    if isinstance(distributor, dict):
                        supplier = distributor.get("distributor_name", "")
                    else:
                        supplier = str(distributor)
                    
                    if not supplier:
                        supplier = "Unknown Supplier"
                    
                    # 获取零件信息
                    part_number = item.get("part_number", ic_model)
                    manufacturer = item.get("manufacturer", "")
                    
                    # 获取库存数量
                    stock_qty = str(item.get("quantity_in_stock", "0"))
                    
                    # 获取最小订购量
                    moq = str(item.get("moq", "1"))
                    
                    # 获取购买链接
                    link = item.get("buy_now_url", "")
                    
                    # 处理价格信息
                    prices = item.get("prices", {})
                    
                    if prices and isinstance(prices, dict):
                        for currency, price_list in prices.items():
                            if isinstance(price_list, list):
                                for price_item in price_list[:3]:  # 每个货币最多取3个价格
                                    unit_price = price_item.get("unit_price")
                                    if unit_price:
                                        # 清理价格字符串
                                        price_str = str(unit_price)
                                        # 提取数字部分
                                        price_match = re.search(r'[\d,.]+', price_str)
                                        if price_match:
                                            price_clean = price_match.group().replace(',', '')
                                            try:
                                                price_float = float(price_clean)
                                            except:
                                                price_float = 0.0
                                            
                                            # 标准化货币代码
                                            currency_upper = currency.upper()
                                            currency_map = {
                                                "USD": "USD", "US$": "USD", "$": "USD",
                                                "EUR": "EUR", "€": "EUR",
                                                "GBP": "GBP", "£": "GBP",
                                                "CNY": "CNY", "RMB": "CNY", "¥": "CNY",
                                                "JPY": "JPY",
                                                "KRW": "KRW", "₩": "KRW"
                                            }
                                            currency_code = currency_map.get(currency_upper, "USD")
                                            
                                            quotes.append({
                                                "supplier": supplier,
                                                "part_number": part_number,
                                                "manufacturer": manufacturer,
                                                "price": str(price_float),
                                                "currency": currency_code,
                                                "stock": stock_qty,
                                                "moq": moq,
                                                "lead_time": item.get("lead_time", ""),
                                                "link": link,
                                                "source": "OEMSecrets API",
                                                "rmb": 0.0,
                                            })
                    
                    # 如果没有价格信息，至少添加一个基础记录
                    if not quotes or quotes[-1].get("part_number") != part_number:
                        quotes.append({
                            "supplier": supplier,
                            "part_number": part_number,
                            "manufacturer": manufacturer,
                            "price": "",
                            "currency": "USD",
                            "stock": stock_qty,
                            "moq": moq,
                            "lead_time": "",
                            "link": link,
                            "source": "OEMSecrets API",
                            "rmb": 0.0,
                        })
                
                _logger.info(f"OEMSecrets API 最终生成 {len(quotes)} 个报价")
                
            elif response.status_code != 200:
                error_msg = response.text[:500] if response.text else "No error message"
                _logger.warning(f"OEMSecrets API error: {response.status_code} - {error_msg}")
                
        except Exception as e:
            _logger.warning(f"OEMSecrets API query failed: {e}")
            import traceback
            traceback.print_exc()
            
        return quotes
    
    @staticmethod
    def _query_nexar_api(ic_model: str, client_id: str, client_secret: str) -> List[Dict]:
        """Query Nexar API"""
        quotes = []
        try:
            import requests
            
            auth_url = "https://api.nexar.com/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }
            
            auth_resp = requests.post(auth_url, data=auth_data, timeout=10)
            _logger.info(f"Nexar auth response status: {auth_resp.status_code}")
            if auth_resp.status_code != 200:
                return quotes
            
            token = auth_resp.json().get("access_token")
            if not token:
                return quotes
            
            query = """
            query Search($mpn: String!) {
                supSearchMpn(searchMpn: $mpn, limit: 10) {
                    results {
                        mpn
                        manufacturer
                        description
                        prices {
                            price
                            currency
                            quantity
                        }
                        stock {
                            stockLevel
                            stockType
                        }
                        partUrl
                    }
                }
            }
            """
            
            headers = {"token": token}
            variables = {"mpn": ic_model}
            
            resp = requests.post(
                "https://api.nexar.com/supply",
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=15
            )
            _logger.info(f"Nexar query response status: {resp.status_code}, text: {resp.text[:200] if resp.text else 'empty'}")
            
            if resp.status_code == 200:
                result = resp.json()
                if "errors" in result:
                    _logger.warning(f"Nexar API errors: {result.get('errors')}")
                    return quotes
                parts = result.get("data", {}).get("supSearchMpn", {}).get("results", [])
                for part in parts:
                    prices = part.get("prices", [])
                    stock = part.get("stock", {})
                    price_info = prices[0] if prices else {}
                    
                    quotes.append({
                        "supplier": "Nexar",
                        "part_number": part.get("mpn", ic_model),
                        "manufacturer": part.get("manufacturer", ""),
                        "price": str(price_info.get("price", "")),
                        "currency": price_info.get("currency", "USD"),
                        "stock": str(stock.get("stockLevel", "")),
                        "moq": str(price_info.get("quantity", "")),
                        "lead_time": "",
                        "link": part.get("partUrl", ""),
                        "source": "Nexar API",
                        "rmb": 0.0,
                    })
        except Exception as e:
            _logger.warning(f"Nexar API query failed: {e}")
        return quotes
    
    @staticmethod
    def _query_lcsc_crawler(ic_model: str) -> List[Dict]:
        """Query LCSC by scraping (fallback)"""
        quotes = []
        try:
            from bs4 import BeautifulSoup
            import requests
            
            url = f"https://www.lcsc.com/search?keyword={ic_model}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            _logger.info(f"LCSC crawler response status: {response.status_code}, text length: {len(response.text)}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                products = soup.select('.product-item')[:10]
                
                if not products:
                    _logger.info(f"LCSC: No products found with selector '.product-item', trying alternative selectors")
                    products = soup.select('.product-list-item')[:10]
                if not products:
                    _logger.info(f"LCSC: Trying to parse product cards directly")
                    products = soup.select('[class*="product"]')[:10]
                
                for product in products:
                    try:
                        price_elem = product.select_one('.price')
                        stock_elem = product.select_one('.stock')
                        
                        quotes.append({
                            "supplier": "LCSC",
                            "part_number": ic_model,
                            "manufacturer": "",
                            "price": price_elem.get_text(strip=True) if price_elem else "",
                            "currency": "CNY",
                            "stock": stock_elem.get_text(strip=True) if stock_elem else "",
                            "moq": "1",
                            "lead_time": "",
                            "link": "",
                            "source": "LCSC Crawler",
                            "rmb": 0.0,
                        })
                    except:
                        continue
        except Exception as e:
            _logger.warning(f"LCSC crawler failed: {e}")
        return quotes
    
    @staticmethod
    def _call_qwen_for_supplement(ic_model: str, qwen_api_key: str) -> List[Dict]:
        """Call Qwen AI for supplementary price queries"""
        quotes = []
        try:
            import requests
            
            prompt = f"""
请搜索IC型号 "{ic_model}" 的价格信息，返回JSON格式。

返回格式：
[
  {{
    "supplier": "供应商名称",
    "part_number": "型号",
    "manufacturer": "品牌",
    "price": "价格数字",
    "currency": "货币(USD/CNY)",
    "stock": "库存数量",
    "moq": "最小订购量",
    "lead_time": "交货期",
    "link": "产品链接"
  }}
]

只返回JSON数组，不要其他文字。
"""
            
            headers = {
                "Authorization": f"Bearer {qwen_api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": "qwen-plus",
                "messages": [
                    {"role": "system", "content": "你是专业的电子元器件价格查询助手，严格返回JSON格式。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            _logger.info(f"Qwen API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                start = content.find("[")
                end = content.rfind("]")
                if start != -1 and end != -1:
                    json_str = content[start:end+1]
                    results = json.loads(json_str)
                    
                    for r in results:
                        if r.get("price"):
                            r["source"] = "Qwen AI"
                            r["rmb"] = 0.0
                            quotes.append(r)
        except Exception as e:
            _logger.warning(f"Qwen query failed: {e}")
        return quotes
    
    @api.model
    def query_prices_with_apis(self, ic_model: str, config_data: Dict, force_refresh: bool = False) -> Dict:
        """Query prices using APIs"""
        _logger.info(f"Querying prices for: {ic_model}, force_refresh: {force_refresh}")
        
        all_quotes = []
        rates = self._get_exchange_rates()
        
        DEFAULT_KEYS = {
            'mouser_api_key': '44f969dc-f1bb-49dc-a2ac-a77d1788d0a6',
            'nexar_client_id': '97a2467a-4520-4fb8-949d-af46f789abce',
            'nexar_client_secret': 'F2A3V7lbSfLB_HV0dVbC2PqI-OA-nAy-xLIs',
            'oemsecrets_api_key': '0shav3t7mz0ik9cg32zx1cucst00nqs20858df6s2k6nnt6nadjhzycjqxuojv4e',
            'qwen_api_key': 'sk-4b767ecd4c414df5a9aa948617dff88a',
        }
        
        # Only use Mouser, OEMSecrets, and Qwen (disable Nexar and LCSC)
        mouser_key = config_data.get('mouser_api_key') or DEFAULT_KEYS.get('mouser_api_key')
        _logger.info(f"Using Mouser key: {bool(mouser_key)}")
        if mouser_key:
            quotes = PriceAPIIntegration._query_mouser_api(ic_model, mouser_key)
            all_quotes.extend(quotes)
            _logger.info(f"Mouser returned {len(quotes)} results")
        
        oemsecrets_key = config_data.get('oemsecrets_api_key') or DEFAULT_KEYS.get('oemsecrets_api_key')
        _logger.info(f"Using OEMSecrets key: {bool(oemsecrets_key)}")
        if oemsecrets_key:
            quotes = PriceAPIIntegration._query_oemsecrets_api(ic_model, oemsecrets_key)
            all_quotes.extend(quotes)
            _logger.info(f"OEMSecrets returned {len(quotes)} results")
        
        # Nexar disabled
        # nexar_id = config_data.get('nexar_client_id') or DEFAULT_KEYS.get('nexar_client_id')
        # nexar_secret = config_data.get('nexar_client_secret') or DEFAULT_KEYS.get('nexar_client_secret')
        
        # LCSC disabled - requires more complex parsing
        # quotes = PriceAPIIntegration._query_lcsc_crawler(ic_model)
        # all_quotes.extend(quotes)
        
        qwen_key = config_data.get('qwen_api_key') or DEFAULT_KEYS.get('qwen_api_key')
        _logger.info(f"Using Qwen key: {bool(qwen_key)}")
        if qwen_key:
            quotes = PriceAPIIntegration._call_qwen_for_supplement(ic_model, qwen_key)
            all_quotes.extend(quotes)
            _logger.info(f"Qwen returned {len(quotes)} results")
        
        for quote in all_quotes:
            try:
                price = float(str(quote.get("price", "0")).replace(",", ""))
                currency = quote.get("currency", "USD")
                quote["rmb"] = PriceAPIIntegration._convert_to_rmb_static(price, currency, rates)
            except:
                quote["rmb"] = 0.0
        
        # 按RMB价格排序（从小到大）
        all_quotes.sort(key=lambda x: x.get("rmb", float('inf')))
        
        _logger.info(f"Final result: {len(all_quotes)} quotes found, sorted by RMB price")
        
        result = {
            "ic_model": ic_model,
            "query_time": datetime.now().isoformat(),
            "count": len(all_quotes),
            "quotes": all_quotes,
            "status": "success" if all_quotes else "error",
            "message": f"Found {len(all_quotes)} quotes from APIs" if all_quotes else "No price data found from any supplier API. Please check API keys and try again.",
        }
        
        return result
    
    @api.model
    def test_api_connection(self, config_data: Dict) -> Dict:
        """Test API connections"""
        results = {
            "redis": {"status": "unknown", "message": "Not tested"},
            "mouser": {"status": "unknown", "message": "Not tested"},
            "nexar": {"status": "unknown", "message": "Not tested"},
            "oemsecrets": {"status": "unknown", "message": "Not tested"},
            "qwen": {"status": "unknown", "message": "Not tested"},
        }
        
        # Test Redis connection
        try:
            import redis
            redis_client = redis.Redis(
                host=config_data.get('redis_host', '127.0.0.1'),
                port=config_data.get('redis_port', 6379),
                password=config_data.get('redis_password', ''),
                db=config_data.get('redis_db', 0),
                decode_responses=True,
            )
            redis_client.ping()
            results["redis"] = {"status": "success", "message": "Connected successfully"}
        except Exception as e:
            results["redis"] = {"status": "error", "message": str(e)}
        
        # Test Mouser API (basic test)
        if config_data.get('mouser_api_key'):
            results["mouser"] = {"status": "configured", "message": "API key provided"}
        else:
            results["mouser"] = {"status": "not_configured", "message": "No API key"}
        
        # Test Nexar API (basic test)
        if config_data.get('nexar_client_id') and config_data.get('nexar_client_secret'):
            results["nexar"] = {"status": "configured", "message": "Client credentials provided"}
        else:
            results["nexar"] = {"status": "not_configured", "message": "Missing client credentials"}
        
        # Test OEMSecrets API (basic test)
        if config_data.get('oemsecrets_api_key'):
            results["oemsecrets"] = {"status": "configured", "message": "API key provided"}
        else:
            results["oemsecrets"] = {"status": "not_configured", "message": "No API key"}
        
        # Test Qwen API (basic test)
        if config_data.get('qwen_api_key'):
            results["qwen"] = {"status": "configured", "message": "API key provided"}
        else:
            results["qwen"] = {"status": "not_configured", "message": "No API key"}
        
        return results