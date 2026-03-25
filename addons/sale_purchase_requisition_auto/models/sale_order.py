# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_insufficient_stock_lines(self):
        self.ensure_one()
        lines_to_order = []
        
        for line in self.order_line:
            if not line.product_id:
                continue
            product = line.product_id
            
            # 使用 qty_available 获取总库存
            available_qty = product.qty_available or 0
            
            if available_qty < line.product_uom_qty:
                missing_qty = line.product_uom_qty - available_qty
                lines_to_order.append({
                    'product_id': product.id,
                    'ordered_qty': line.product_uom_qty,
                    'available_qty': available_qty,
                    'missing_qty': missing_qty,
                })
        return lines_to_order

    def action_create_requisition(self):
        self.ensure_one()
        
        lines_to_order = self._get_insufficient_stock_lines()
        
        if not lines_to_order:
            raise UserError(_('所有产品库存充足，无需创建采购需求单。'))
        
        # 如果只有一行，直接创建并打开向导
        if len(lines_to_order) == 1:
            line = lines_to_order[0]
            product = self.env['product.product'].browse(line['product_id'])
            
            # 自动选择供应商
            vendor_id = False
            if product.seller_ids:
                vendor_id = product.seller_ids[0].partner_id.id
            
            wizard_id = self.env['sale.order.requisition.wizard'].create({
                'order_id': self.id,
                'product_id': line['product_id'],
                'ordered_qty': line['ordered_qty'],
                'available_qty': line['available_qty'],
                'missing_qty': line['missing_qty'],
                'qty_type': 'missing',
                'vendor_id': vendor_id,
            })
            
            return {
                'name': _('创建采购订单'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order.requisition.wizard',
                'view_mode': 'form',
                'target': 'new',
                'res_id': wizard_id.id,
            }
        
        # 多行：创建多个向导记录
        wizard_ids = []
        for line in lines_to_order:
            product = self.env['product.product'].browse(line['product_id'])
            vendor_id = False
            if product.seller_ids:
                vendor_id = product.seller_ids[0].partner_id.id
                
            wizard_id = self.env['sale.order.requisition.wizard'].create({
                'order_id': self.id,
                'product_id': line['product_id'],
                'ordered_qty': line['ordered_qty'],
                'available_qty': line['available_qty'],
                'missing_qty': line['missing_qty'],
                'qty_type': 'missing',
                'vendor_id': vendor_id,
            })
            wizard_ids.append(wizard_id.id)
        
        # 打开向导列表
        return {
            'name': _('创建采购订单'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.requisition.wizard',
            'view_mode': 'tree,form',
            'target': 'new',
            'domain': [('id', 'in', wizard_ids)],
        }
