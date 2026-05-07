# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_requisition(self):
        self.ensure_one()
        
        lines_to_order = []
        for line in self.order_line:
            if not line.product_id:
                continue
            lines_to_order.append({
                'product_id': line.product_id.id,
                'ordered_qty': line.product_uom_qty,
            })
        
        if not lines_to_order:
            raise UserError(_('没有产品需要创建采购订单。'))
        
        vendor_id = False
        
        vendor_id = False
        po_lines = []
        
        for line in lines_to_order:
            product = self.env['product.product'].browse(line['product_id'])
            qty = line['ordered_qty']
            
            tmpl = product.product_tmpl_id
            responsible = tmpl.purchase_responsible_id
            if responsible and responsible.partner_id:
                vendor_id = responsible.partner_id.id
            
            if not vendor_id and product.seller_ids and product.seller_ids[0].partner_id:
                vendor_id = product.seller_ids[0].partner_id.id
            
            po_lines.append((0, 0, {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom_id': product.uom_id.id,
                'price_unit': product.standard_price or 0,
                'name': product.display_name,
            }))
            
            if vendor_id:
                break
        
        if not vendor_id:
            purchase_users = self.env['res.users'].search([
                ('group_ids', 'in', self.env.ref('purchase.group_purchase_user').id)
            ], limit=1)
            if purchase_users and purchase_users.partner_id:
                vendor_id = purchase_users.partner_id.id
        
        if not vendor_id:
            all_partners = self.env['res.partner'].search([], limit=1)
            if all_partners:
                vendor_id = all_partners[0].id
        
        if not vendor_id:
            raise UserError(_('没有可用供应商，请在系统中创建供应商。'))
        
        po_vals = {
            'origin': self.name,
            'user_id': self.env.user.id,
            'partner_id': vendor_id,
            'order_line': po_lines,
        }
        
        po = self.env['purchase.order'].create(po_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
        }
