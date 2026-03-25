from odoo import http
from odoo.http import request, content_disposition
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
_logger.info("PriceController module loaded")

class PriceController(http.Controller):
    
    def __init__(self):
        _logger.info("PriceController class initialized")
    
    @http.route('/price/test', type='http', auth='public')
    def test_page(self, **kwargs):
        _logger.info("PriceController.test_page called")
        return "Price module test page - OK"
    
    @http.route('/price/hello', type='http', auth='public')
    def hello(self, **kwargs):
        _logger.info("PriceController.hello called")
        return "Hello from Price Module!"
    
    @http.route('/zh_CN/price/query', type='http', auth='user')
    def price_query_page(self, **kwargs):
        error = kwargs.get('error')
        return request.render('custom_price_module.price_query_page', {
            'error': error
        })
    
    @http.route('/price/query', type='http', auth='user')
    def price_query_page_en(self, **kwargs):
        error = kwargs.get('error')
        return request.render('custom_price_module.price_query_page', {
            'error': error
        })
    
    @http.route('/zh_CN/price/config', type='http', auth='user', website=True)
    def config_page(self, **kwargs):
        config = request.env['price.query'].get_config()
        success = kwargs.get('success')
        return request.render('custom_price_module.config_page', {
            'config': config,
            'success': success
        })
    
    @http.route('/price/config', type='http', auth='user', website=True)
    def config_page_en(self, **kwargs):
        config = request.env['price.query'].get_config()
        success = kwargs.get('success')
        return request.render('custom_price_module.config_page', {
            'config': config,
            'success': success
        })
    
    @http.route('/zh_CN/price/query/submit', type='http', auth='user', website=True, csrf=False)
    def price_query_submit(self, **kwargs):
        ic_model = kwargs.get('ic_model', '').strip()
        force_refresh = kwargs.get('refresh') == 'true'
        
        if not ic_model:
            return request.redirect('/zh_CN/price/query?error=Please+enter+an+IC+model')
        
        try:
            price_model = request.env['price.query']
            result = price_model.query_prices(ic_model, force_refresh)
            
            return request.render('custom_price_module.price_result_page', {
                'ic_model': ic_model,
                'status': result.get('status', 'unknown'),
                'message': result.get('message', ''),
                'query_time': result.get('query_time', ''),
                'count': result.get('count', 0),
                'quotes': result.get('quotes', []),
            })
        except Exception as e:
            return request.redirect(f'/zh_CN/price/query?error=Error+querying+prices:+{str(e)}')
    
    @http.route('/price/query/submit', type='http', auth='user', website=True, csrf=False)
    def price_query_submit_en(self, **kwargs):
        ic_model = kwargs.get('ic_model', '').strip()
        force_refresh = kwargs.get('refresh') == 'true'
        
        if not ic_model:
            return request.redirect('/price/query?error=Please+enter+an+IC+model')
        
        try:
            price_model = request.env['price.query']
            result = price_model.query_prices(ic_model, force_refresh)
            
            return request.render('custom_price_module.price_result_page', {
                'ic_model': ic_model,
                'status': result.get('status', 'unknown'),
                'message': result.get('message', ''),
                'query_time': result.get('query_time', ''),
                'count': result.get('count', 0),
                'quotes': result.get('quotes', []),
            })
        except Exception as e:
            return request.redirect(f'/price/query?error=Error+querying+prices:+{str(e)}')
    
    @http.route('/zh_CN/price/download/csv/<string:ic_model>', type='http', auth='user')
    def download_csv(self, ic_model, **kwargs):
        try:
            price_model = request.env['price.query']
            result = price_model.query_prices(ic_model)
            quotes = result.get('quotes', [])
            
            if not quotes:
                return request.redirect('/zh_CN/price/query?error=No+quotes+found+to+download')
            
            csv_lines = ['Supplier,Part Number,Description,Manufacturer,Currency,Price,RMB,Stock,MOQ,Lead Time,Source,Link']
            
            for quote in quotes:
                supplier = quote.get('supplier', '')
                part_number = quote.get('part_number', '')
                description = quote.get('description', '')
                manufacturer = quote.get('manufacturer', '')
                currency = quote.get('currency', '')
                price = quote.get('price', '')
                rmb = quote.get('rmb', '')
                stock = quote.get('stock', '')
                moq = quote.get('moq', '')
                lead_time = quote.get('lead_time', '')
                source = quote.get('source', '')
                link = quote.get('link', '')
                
                csv_line = f'"{supplier}","{part_number}","{description}","{manufacturer}","{currency}",{price},{rmb},"{stock}",{moq},"{lead_time}","{source}","{link}"'
                csv_lines.append(csv_line)
            
            csv_content = '\n'.join(csv_lines)
            
            filename = f'price_quotes_{ic_model}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            headers = [
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', content_disposition(filename))
            ]
            
            return request.make_response(csv_content, headers=headers)
            
        except Exception as e:
            return request.redirect(f'/zh_CN/price/query?error=Error+generating+CSV:+{str(e)}')
    
    @http.route('/price/download/csv/<string:ic_model>', type='http', auth='user')
    def download_csv_en(self, ic_model, **kwargs):
        try:
            price_model = request.env['price.query']
            result = price_model.query_prices(ic_model)
            quotes = result.get('quotes', [])
            
            if not quotes:
                return request.redirect('/price/query?error=No+quotes+found+to+download')
            
            csv_lines = ['Supplier,Part Number,Description,Manufacturer,Currency,Price,RMB,Stock,MOQ,Lead Time,Source,Link']
            
            for quote in quotes:
                supplier = quote.get('supplier', '')
                part_number = quote.get('part_number', '')
                description = quote.get('description', '')
                manufacturer = quote.get('manufacturer', '')
                currency = quote.get('currency', '')
                price = quote.get('price', '')
                rmb = quote.get('rmb', '')
                stock = quote.get('stock', '')
                moq = quote.get('moq', '')
                lead_time = quote.get('lead_time', '')
                source = quote.get('source', '')
                link = quote.get('link', '')
                
                csv_line = f'"{supplier}","{part_number}","{description}","{manufacturer}","{currency}",{price},{rmb},"{stock}",{moq},"{lead_time}","{source}","{link}"'
                csv_lines.append(csv_line)
            
            csv_content = '\n'.join(csv_lines)
            
            filename = f'price_quotes_{ic_model}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            headers = [
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', content_disposition(filename))
            ]
            
            return request.make_response(csv_content, headers=headers)
            
        except Exception as e:
            return request.redirect(f'/price/query?error=Error+generating+CSV:+{str(e)}')
    
    @http.route('/zh_CN/price/config/save', type='http', auth='user', website=True, csrf=False)
    def config_save(self, **kwargs):
        try:
            config = request.env['price.query'].get_config()
            
            update_data = {}
            if 'mouser_api_key' in kwargs:
                update_data['mouser_api_key'] = kwargs['mouser_api_key']
            if 'nexar_client_id' in kwargs:
                update_data['nexar_client_id'] = kwargs['nexar_client_id']
            if 'nexar_client_secret' in kwargs:
                update_data['nexar_client_secret'] = kwargs['nexar_client_secret']
            if 'oemsecrets_api_key' in kwargs:
                update_data['oemsecrets_api_key'] = kwargs['oemsecrets_api_key']
            if 'qwen_api_key' in kwargs:
                update_data['qwen_api_key'] = kwargs['qwen_api_key']
            
            if update_data:
                config.write(update_data)
            
            return request.redirect('/zh_CN/price/config?success=Configuration+saved+successfully')
            
        except Exception as e:
            return request.redirect(f'/zh_CN/price/config?error=Error+saving+configuration:+{str(e)}')
    
    @http.route('/price/config/save', type='http', auth='user', website=True, csrf=False)
    def config_save_en(self, **kwargs):
        try:
            config = request.env['price.query'].get_config()
            
            update_data = {}
            if 'mouser_api_key' in kwargs:
                update_data['mouser_api_key'] = kwargs['mouser_api_key']
            if 'nexar_client_id' in kwargs:
                update_data['nexar_client_id'] = kwargs['nexar_client_id']
            if 'nexar_client_secret' in kwargs:
                update_data['nexar_client_secret'] = kwargs['nexar_client_secret']
            if 'oemsecrets_api_key' in kwargs:
                update_data['oemsecrets_api_key'] = kwargs['oemsecrets_api_key']
            if 'qwen_api_key' in kwargs:
                update_data['qwen_api_key'] = kwargs['qwen_api_key']
            
            if update_data:
                config.write(update_data)
            
            return request.redirect('/price/config?success=Configuration+saved+successfully')
            
        except Exception as e:
            return request.redirect(f'/price/config?error=Error+saving+configuration:+{str(e)}')