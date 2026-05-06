from odoo import http
from odoo.http import request
import json
import logging
from urllib.parse import quote_plus

_logger = logging.getLogger(__name__)

class PriceController(http.Controller):
    
    @http.route('/price/test', type='http', auth='public')
    def test_page(self, **kwargs):
        return "Price module test page - OK"
    
    @http.route('/price/query', type='http', auth='public')
    def price_query(self, **kwargs):
        """Direct API endpoint to get price quote for a given IC model"""
        ic_model = kwargs.get('ic_model', '').strip()
        
        if not ic_model:
            # Get first product as default
            product = request.env['product.product'].sudo().search([], limit=1)
            if product:
                ic_model = product.default_code or product.name or 'STM32F103C8T6'
            else:
                ic_model = 'STM32F103C8T6'
        
        try:
            _logger.info(f"Querying price for: {ic_model}")
            price_model = request.env['price.query'].sudo()
            result = price_model.query_prices(ic_model)
            _logger.info(f"Query result: status={result.get('status')}, count={result.get('count')}")
            
            # Return JSON response
            return request.make_response(
                json.dumps(result, ensure_ascii=False),
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
        except Exception as e:
            _logger.error(f"Price query error: {e}", exc_info=True)
            return request.make_response(
                json.dumps({'error': str(e), 'status': 'error'}),
                headers=[('Content-Type', 'application/json')]
            )

    @http.route(['/zh_CN/price/query/submit', '/price/query/submit'], type='http', auth='user', website=True, csrf=False)
    def price_query_submit(self, **kwargs):
        ic_model = kwargs.get('ic_model', '').strip()
        force_refresh = kwargs.get('refresh') == 'true'
        if not ic_model:
            redirect_path = '/zh_CN/price/query' if request.httprequest.path.startswith('/zh_CN') else '/price/query'
            return request.redirect(f'{redirect_path}?error=Please+enter+an+IC+model')

        try:
            price_model = request.env['price.query'].sudo()
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
            redirect_path = '/zh_CN/price/query' if request.httprequest.path.startswith('/zh_CN') else '/price/query'
            return request.redirect(f'{redirect_path}?error=Error+querying+prices:+{quote_plus(str(e))}')

    @http.route('/price_query_iframe', type='http', auth='user', website=True)
    def price_query_iframe(self, **kwargs):
        ic_model = kwargs.get('ic_model', '').strip()
        if not ic_model:
            return request.redirect('/price/query?error=Please+enter+an+IC+model')
        refresh = 'true' if kwargs.get('refresh') == 'true' else 'false'
        return request.redirect(f'/price/query/submit?ic_model={quote_plus(ic_model)}&refresh={refresh}')