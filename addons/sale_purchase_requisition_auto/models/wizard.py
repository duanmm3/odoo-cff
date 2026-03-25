# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderRequisitionWizard(models.TransientModel):
    _name = 'sale.order.requisition.wizard'
    _description = '创建采购订单向导'

    order_id = fields.Many2one(
        'sale.order',
        string='销售订单',
        required=True,
        readonly=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='产品',
        readonly=True
    )
    ordered_qty = fields.Float(
        string='订单数量',
        readonly=True
    )
    available_qty = fields.Float(
        string='可用库存',
        readonly=True
    )
    missing_qty = fields.Float(
        string='缺少数量',
        readonly=True
    )
    qty_type = fields.Selection([
        ('missing', '缺少数量'),
        ('full', '订单全量'),
    ], string='采购数量类型', default='missing', required=True)
    
    vendor_id = fields.Many2one(
        'res.partner',
        string='采购员',
        help='负责此产品采购的人员'
    )
    
    send_notification = fields.Boolean(
        string='通知采购负责人',
        default=True,
        help='勾选后，将向采购负责人发送Odoo内部消息通知'
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # 自动选择第一个供应商
            sellers = self.product_id.seller_ids
            if sellers:
                self.vendor_id = sellers[0].partner_id

    def action_create_purchase_order(self):
        self.ensure_one()
        
        if self.qty_type == 'full':
            qty = self.ordered_qty
        else:
            qty = self.missing_qty
        
        if qty <= 0:
            raise UserError(_('没有有效的产品需要创建采购订单。'))
        
        product = self.product_id
        
        # 自动确定供应商
        vendor_id = False
        # 1. 优先使用采购负责人
        responsible = (
            product.product_tmpl_id.purchase_responsible_id or
            product.responsible_id
        )
        if responsible and responsible.partner_id:
            vendor_id = responsible.partner_id.id
        
        # 2. 如果没有负责人，使用产品的供应商
        if not vendor_id and product.seller_ids:
            vendor_id = product.seller_ids[0].partner_id.id
        
        # 创建采购订单
        po_vals = {
            'origin': self.order_id.name,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom_id': product.uom_id.id,
                'price_unit': product.standard_price,
                'date_planned': fields.Date.context_today(self),
            })],
        }
        if vendor_id:
            po_vals['partner_id'] = vendor_id
            
        po = self.env['purchase.order'].create(po_vals)
        
        # 发送通知
        if self.send_notification and responsible and responsible.partner_id:
            vendor_name = self.env['res.partner'].browse(vendor_id).name if vendor_id else '未指定'
            self.order_id.message_post(
                body=_('''
                    <b>已创建采购订单</b><br/>
                    采购订单: <a href="/web#model=purchase.order&id=%d">%s</a><br/>
                    来源销售订单: %s<br/>
                    产品: %s<br/>
                    采购数量: %.0f<br/>
                    供应商: %s
                ''' % (po.id, po.name, self.order_id.name, product.name, qty, vendor_name)),
                subject=_('【采购提醒】销售订单 %s 库存不足') % self.order_id.name,
                partner_ids=[responsible.partner_id.id],
                message_type='notification',
            )
        
        return {
            'type': 'ir.actions.act_window_close',
            'infos': {'done': True},
        }
