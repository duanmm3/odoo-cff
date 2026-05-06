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
        }
        
        _logger.info(f"Using API keys - mouser: {bool(config_data['mouser_api_key'])}, oemsecrets: {bool(config_data['oemsecrets_api_key'])}, qwen: {bool(config_data['qwen_api_key'])}")
        _logger.info(f"Calling API integration for: {ic_model}")
        
        # Call API integration
        api_model = self.env['price.api.integration']
        result = api_model.query_prices_with_apis(ic_model, config_data, force_refresh)
        
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
        """View the recent query records for this IC model"""
        self.ensure_one()
        history_records = self.search([('name', '=', self.name)], order='query_date desc')
        
        message = _('Recent query records for %s:\n') % self.name
        for record in history_records[:5]:
            query_time = record.query_date.strftime('%Y-%m-%d %H:%M:%S') if record.query_date else _('Unknown')
            message += _('- %s: %s quotes\n') % (query_time, record.total_quotes or 0)
        
        if len(history_records) > 5:
            message += _('... and %d more') % (len(history_records) - 5)
        
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
        try:
            redis_client = self.get_redis_client()
            if redis_client:
                pattern = f"Price:IC:{self.name}:*"
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    _logger.info(f"Cleared cache for {self.name}: {len(keys)} keys")
        except Exception as e:
            _logger.warning(f"Redis clear_cache error: {e}")
        
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