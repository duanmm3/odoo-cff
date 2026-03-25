# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
供应商Portal报价模块
"""

from odoo import http
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class VendorPortal(CustomerPortal):
    """供应商门户"""

    @route([
        '/my/rfq',
        '/my/rfq/<int:order_id>',
    ], type='http', auth='user', website=True)
    def portal_my_rfq(self, order_id=None, **kwargs):
        """供应商查看待报价的RFQ"""
        partner = request.env.user.partner_id
        
        # 获取该供应商待报价的RFQ
        orders = request.env['purchase.order'].search([
            ('partner_id', '=', partner.id),
            ('state', 'in', ['draft', 'sent']),
            ('quote_stage', 'in', ['primary_contact', 'bidding']),
        ])
        
        values = {
            'orders': orders,
            'page_name': 'rfq',
        }
        return request.render('custom_smart_rfq_notify.portal_my_rfq', values)

    @route('/my/rfq/<int:order_id>/quote', type='http', auth='user', website=True)
    def portal_quote_rfq(self, order_id, **kwargs):
        """供应商报价页面"""
        order = request.env['purchase.order'].browse(order_id)
        partner = request.env.user.partner_id
        
        # 验证权限
        if order.partner_id != partner:
            return request.redirect('/my/rfq')
        
        values = {
            'order': order,
            'page_name': 'rfq_quote',
        }
        return request.render('custom_smart_rfq_notify.portal_quote_rfq', values)

    @route('/my/rfq/<int:order_id>/submit_quote', type='http', auth='user', 
            website=True, methods=['POST'])
    def portal_submit_quote(self, order_id, **kwargs):
        """供应商提交报价"""
        order = request.env['purchase.order'].browse(order_id)
        partner = request.env.user.partner_id
        
        # 验证权限
        if order.partner_id != partner:
            return request.redirect('/my/rfq')
        
        # 解析报价数据
        quote_data = {}
        for key, value in kwargs.items():
            if key.startswith('price_'):
                line_id = key.replace('price_', '')
                if not quote_data.get(line_id):
                    quote_data[line_id] = {}
                quote_data[line_id]['price_unit'] = float(value)
            elif key.startswith('date_'):
                line_id = key.replace('date_', '')
                if not quote_data.get(line_id):
                    quote_data[line_id] = {}
                quote_data[line_id]['date_planned'] = value
        
        # 创建报价记录
        quote = request.env['purchase.order.quote'].create({
            'order_id': order.id,
            'vendor_id': partner.id,
            'currency_id': order.currency_id.id,
            'note': kwargs.get('note', ''),
        })
        
        # 创建报价明细
        for line in order.order_line:
            if line.display_type:
                continue
            line_data = quote_data.get(str(line.id), {})
            request.env['purchase.order.quote.line'].create({
                'quote_id': quote.id,
                'product_id': line.product_id.id,
                'product_qty': line_data.get('product_qty', line.product_qty),
                'product_uom_id': line_data.get('product_uom_id', line.product_uom.id),
                'price_unit': line_data.get('price_unit', line.price_unit),
                'tax_ids': [(6, 0, line.tax_ids.ids)],
                'currency_id': order.currency_id.id,
            })
        
        # 更新订单状态
        order.write({'quote_stage': 'quoted'})
        
        # 发送通知给销售
        order.message_post(
            body=f'供应商 {partner.name} 提交了报价',
            subject='供应商报价通知'
        )
        
        return request.redirect(f'/my/rfq/{order_id}?success=1')
