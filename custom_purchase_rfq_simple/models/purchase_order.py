# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
简化版: 通过销售订单关联判断RFQ来源
"""

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # 关联的销售订单（如果有）
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Source Sale Order',
        copy=False,
        index=True
    )

    # 是否来自销售
    is_from_sale = fields.Boolean(
        string='From Sales',
        compute='_compute_is_from_sale',
        store=True
    )

    @api.depends('sale_order_id', 'origin')
    def _compute_is_from_sale(self):
        """判断RFQ是否来自销售"""
        for order in self:
            # 通过关联销售订单判断
            if order.sale_order_id:
                order.is_from_sale = True
                continue
            
            # 或者通过源文档判断
            if order.origin and 'sale.order' in order.origin.lower():
                order.is_from_sale = True
                continue
            
            order.is_from_sale = False

    def write(self, vals):
        """控制价格修改权限"""
        price_fields = ['price_unit', 'product_qty', 'discount']
        
        if any(field in vals for field in price_fields):
            current_user = self.env.user
            purchase_group = self.env.ref('purchase.group_purchase_user', False)
            sale_group = self.env.ref('sales_team.group_sale_salesman', False)
            
            is_purchase_user = purchase_group and purchase_group in current_user.groups_id
            is_sale_user = sale_group and sale_group in current_user.groups_id
            
            for order in self:
                # 来自销售的RFQ，采购不能修改
                if (order.is_from_sale and is_purchase_user and not is_sale_user):
                    if order.state in ('draft', 'sent'):
                        raise AccessError(
                            _('此询价单来自销售订单，采购用户无法修改价格。\n'
                              '请联系销售经理处理。')
                        )
        
        return super().write(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def write(self, vals):
        """控制价格修改权限"""
        price_fields = ['price_unit', 'product_qty', 'discount']
        
        if any(field in vals for field in price_fields):
            current_user = self.env.user
            purchase_group = self.env.ref('purchase.group_purchase_user', False)
            sale_group = self.env.ref('sales_team.group_sale_salesman', False)
            
            is_purchase_user = purchase_group and purchase_group in current_user.groups_id
            is_sale_user = sale_group and sale_group in current_user.groups_id
            
            for line in self:
                order = line.order_id
                if (order.is_from_sale and is_purchase_user and not is_sale_user):
                    if order.state in ('draft', 'sent'):
                        raise AccessError(
                            _('此询价单来自销售订单，采购用户无法修改价格。')
                        )
        
        return super().write(vals)
