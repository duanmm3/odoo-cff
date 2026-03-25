from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

_logger = logging.getLogger(__name__)

class PriceQuery(models.Model):
    _name = 'price.query'
    _description = 'IC Price Query'
    _order = 'query_date desc'
    
    name = fields.Char(string='IC Model', required=True, index=True)
    query_date = fields.Datetime(string='Query Date', default=fields.Datetime.now, index=True)
    query_count = fields.Integer(string='Query Count', default=1)
    last_query_result = fields.Text(string='Last Query Result (JSON)')
    last_query_time = fields.Datetime(string='Last Query Time')
    best_price = fields.Float(string='Best Price (RMB)', digits=(12, 4))
    best_supplier = fields.Char(string='Best Supplier')
    total_quotes = fields.Integer(string='Total Quotes Found')
    
    # Configuration fields
    mouser_api_key = fields.Char(string='Mouser API Key', help='API key for Mouser')
    nexar_client_id = fields.Char(string='Nexar Client ID')
    nexar_client_secret = fields.Char(string='Nexar Client Secret')
    oemsecrets_api_key = fields.Char(string='OEMSecrets API Key')
    qwen_api_key = fields.Char(string='Qwen API Key')
    
    # Redis configuration
    redis_host = fields.Char(string='Redis Host', default='127.0.0.1')
    redis_port = fields.Integer(string='Redis Port', default=6379)
    redis_password = fields.Char(string='Redis Password', default='1234abcd')
    redis_db = fields.Integer(string='Redis DB', default=0)
    
    # Exchange rate configuration
    exchange_api_url = fields.Char(
        string='Exchange API URL', 
        default='https://open.er-api.com/v6/latest/USD'
    )
    
    # Status fields
    is_active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def get_config(self):
        """Get system configuration"""
        config = self.search([], limit=1)
        if not config:
            config = self.create({
                'name': 'System Configuration',
                'mouser_api_key': '44f969dc-f1bb-49dc-a2ac-a77d1788d0a6',
                'nexar_client_id': '97a2467a-4520-4fb8-949d-af46f789abce',
                'nexar_client_secret': 'F2A3V7lbSfLB_HV0dVbC2PqI-OA-nAy-xLIs',
                'oemsecrets_api_key': '0shav3t7mz0ik9cg32zx1cucst00nqs20858df6s2k6nnt6nadjhzycjqxuojv4e',
                'qwen_api_key': 'sk-4b767ecd4c414df5a9aa948617dff88a',
            })
            _logger.info(f"Created default config with id: {config.id}")
        else:
            _logger.info(f"Found existing config, mouser_key: {bool(config.mouser_api_key)}, qwen_key: {bool(config.qwen_api_key)}")
        return config
    
    def get_redis_client(self):
        """Get Redis client connection"""
        try:
            import redis
            config = self.get_config()
            return redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=config.redis_db,
                decode_responses=True,
            )
        except ImportError:
            _logger.warning("Redis module not installed")
            return None
        except Exception as e:
            _logger.error(f"Redis connection error: {e}")
            return None
    
    def get_cache(self, ic_model: str, date: str = None) -> Optional[Dict]:
        """Get cached price data"""
        redis_client = self.get_redis_client()
        if not redis_client:
            return None
        
        if not date:
            date = time.strftime("%Y%m%d")
        
        key = f"Price:IC:{ic_model}:{date}"
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                pass
        return None
    
    def set_cache(self, ic_model: str, data: Dict):
        """Set cache with price data"""
        redis_client = self.get_redis_client()
        if not redis_client:
            return
        
        today = time.strftime("%Y%m%d")
        key = f"Price:IC:{ic_model}:{today}"
        value = json.dumps(data, ensure_ascii=False)
        redis_client.set(key, value)
    
    def get_history_dates(self, ic_model: str) -> List[str]:
        """Get historical dates for an IC model"""
        redis_client = self.get_redis_client()
        if not redis_client:
            return []
        
        pattern = f"Price:IC:{ic_model}:*"
        keys = redis_client.keys(pattern)
        
        dates = []
        for key in keys:
            parts = key.split(":")
            if len(parts) >= 4:
                dates.append(parts[3])
        
        return sorted(dates)
    
    def fetch_exchange_rates(self) -> Optional[Dict[str, float]]:
        """Fetch exchange rates from API"""
        try:
            import requests
            config = self.get_config()
            
            resp = requests.get(config.exchange_api_url, timeout=10)
            data = resp.json()
            if data.get("result") == "success":
                rates = data.get("rates", {})
                return {k.upper(): float(v) for k, v in rates.items() if isinstance(v, (int, float))}
        except Exception as e:
            _logger.error(f"Failed to fetch exchange rates: {e}")
        return None
    
    def convert_to_rmb(self, currency: str, amount: float, rates_cache: Dict) -> Optional[float]:
        """Convert currency to RMB"""
        if not currency or not rates_cache:
            return None
        
        cur = currency.upper()
        cur_map = {
            "RMB": "CNY",
            "￥": "CNY",
            "¥": "CNY",
        }
        cur = cur_map.get(cur, cur)
        
        if cur not in rates_cache:
            _logger.warning(f"Exchange rate not found: {currency} -> {cur}")
            return None
        
        usd_rate = rates_cache.get(cur, 1.0)
        cny_rate = rates_cache.get("CNY", 7.2)
        
        usd_amount = amount / usd_rate
        return round(usd_amount * cny_rate, 4)
    
    def query_prices(self, ic_model: str, force_refresh: bool = False) -> Dict:
        """Main query function - uses API integration"""
        # Check cache first
        if not force_refresh:
            cached = self.get_cache(ic_model)
            if cached:
                _logger.info(f"Using cache for: {ic_model}, force_refresh={force_refresh}")
                return cached
            _logger.info(f"No cache found for: {ic_model}, force_refresh={force_refresh}")
        else:
            _logger.info(f"Force refresh enabled for: {ic_model}")
        
        # Get configuration
        config = self.get_config()
        
        DEFAULT_KEYS = {
            'mouser_api_key': '44f969dc-f1bb-49dc-a2ac-a77d1788d0a6',
            'nexar_client_id': '97a2467a-4520-4fb8-949d-af46f789abce',
            'nexar_client_secret': 'F2A3V7lbSfLB_HV0dVbC2PqI-OA-nAy-xLIs',
            'oemsecrets_api_key': '0shav3t7mz0ik9cg32zx1cucst00nqs20858df6s2k6nnt6nadjhzycjqxuojv4e',
            'qwen_api_key': 'sk-4b767ecd4c414df5a9aa948617dff88a',
        }
        
        config_data = {
            'mouser_api_key': config.mouser_api_key or DEFAULT_KEYS['mouser_api_key'],
            'nexar_client_id': config.nexar_client_id or DEFAULT_KEYS['nexar_client_id'],
            'nexar_client_secret': config.nexar_client_secret or DEFAULT_KEYS['nexar_client_secret'],
            'oemsecrets_api_key': config.oemsecrets_api_key or DEFAULT_KEYS['oemsecrets_api_key'],
            'qwen_api_key': config.qwen_api_key or DEFAULT_KEYS['qwen_api_key'],
            'redis_host': config.redis_host or '127.0.0.1',
            'redis_port': config.redis_port or 6379,
            'redis_password': config.redis_password or '1234abcd',
            'redis_db': config.redis_db or 0,
        }
        
        _logger.info(f"Using API keys - mouser: {bool(config_data['mouser_api_key'])}, oemsecrets: {bool(config_data['oemsecrets_api_key'])}, qwen: {bool(config_data['qwen_api_key'])}")
        _logger.info(f"Calling API integration for: {ic_model}")
        
        # Call API integration
        api_model = self.env['price.api.integration']
        result = api_model.query_prices_with_apis(ic_model, config_data, force_refresh)
        
        # Cache the result
        self.set_cache(ic_model, result)
        
        # Update query record
        query_record = self.search([('name', '=', ic_model)], limit=1)
        if query_record:
            query_record.write({
                'last_query_result': json.dumps(result, ensure_ascii=False),
                'last_query_time': fields.Datetime.now(),
                'query_count': query_record.query_count + 1,
            })
        else:
            self.create({
                'name': ic_model,
                'last_query_result': json.dumps(result, ensure_ascii=False),
                'last_query_time': fields.Datetime.now(),
            })
        
        return result
    
    def get_best_price_info(self, ic_model: str) -> Dict:
        """Get best price information for an IC model"""
        result = self.query_prices(ic_model)
        quotes = result.get('quotes', [])
        
        if not quotes:
            return {
                'ic_model': ic_model,
                'best_price': None,
                'best_supplier': None,
                'total_quotes': 0,
                'query_time': result.get('query_time'),
            }
        
        # Find best price (lowest RMB)
        best_quote = None
        best_price = float('inf')
        
        for quote in quotes:
            rmb_price = quote.get('rmb')
            if rmb_price is not None and rmb_price < best_price:
                best_price = rmb_price
                best_quote = quote
        
        return {
            'ic_model': ic_model,
            'best_price': best_price if best_quote else None,
            'best_supplier': best_quote.get('supplier') if best_quote else None,
            'total_quotes': len(quotes),
            'query_time': result.get('query_time'),
        }
    
    def action_query_price(self):
        """Action to query price for current record"""
        self.ensure_one()
        result = self.query_prices(self.name, force_refresh=True)
        
        # Update record with best price info
        best_info = self.get_best_price_info(self.name)
        
        self.write({
            'best_price': best_info.get('best_price'),
            'best_supplier': best_info.get('best_supplier'),
            'total_quotes': best_info.get('total_quotes'),
            'last_query_time': fields.Datetime.now(),
            'last_query_result': json.dumps(result, ensure_ascii=False),
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Price Query'),
                'message': _('Queried %s, found %d quotes') % (self.name, best_info.get('total_quotes', 0)),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_view_history(self):
        """View historical prices for this IC model"""
        self.ensure_one()
        dates = self.get_history_dates(self.name)
        
        history_data = []
        for date in dates:
            cached = self.get_cache(self.name, date)
            if cached:
                history_data.append({
                    'date': date,
                    'count': cached.get('count', 0),
                    'query_time': cached.get('query_time'),
                })
        
        # Return a notification with history info
        message = _('Historical prices for %s:\n') % self.name
        for item in history_data[:5]:  # Show last 5
            message += _('- %s: %d quotes\n') % (item['date'], item['count'])
        
        if len(history_data) > 5:
            message += _('... and %d more') % (len(history_data) - 5)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Price History'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_clear_cache(self):
        """Clear cache for this IC model"""
        self.ensure_one()
        redis_client = self.get_redis_client()
        if redis_client:
            pattern = f"Price:IC:{self.name}:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                _logger.info(f"Cleared cache for {self.name}: {len(keys)} keys")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cache Cleared'),
                'message': _('Cache cleared for %s') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }