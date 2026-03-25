# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # 标记RFQ创建者的类型
    creator_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
    ], string='Creator Type', compute='_compute_creator_type', store=True)

    # 标记是否允许采购用户修改价格
    allow_purchase_edit_price = fields.Boolean(
        string='Allow Purchase Edit Price',
        compute='_compute_allow_purchase_edit_price',
        search='_search_allow_purchase_edit_price'
    )

    @api.depends('create_uid', 'create_uid.groups_id')
    def _compute_creator_type(self):
        """根据创建者所属组确定类型"""
        for order in self:
            user = order.create_uid
            if not user:
                order.creator_type = 'purchase'
                continue
            
            # 检查用户是否属于销售组
            sale_group = self.env.ref('sales_team.group_sale_salesman', False)
            purchase_group = self.env.ref('purchase.group_purchase_user', False)
            
            if sale_group and sale_group in user.groups_id:
                order.creator_type = 'sale'
            elif purchase_group and purchase_group in user.groups_id:
                order.creator_type = 'purchase'
            else:
                order.creator_type = 'purchase'

    @api.depends('creator_type', 'state')
    def _compute_allow_purchase_edit_price(self):
        """计算是否允许采购用户修改价格"""
        for order in self:
            # 销售创建的RFQ，采购不能修改价格
            # 但已确认的订单或草稿状态可能允许
            if order.creator_type == 'sale' and order.state in ('draft', 'sent'):
                order.allow_purchase_edit_price = False
            else:
                order.allow_purchase_edit_price = True

    def _search_allow_purchase_edit_price(self, operator, value):
        """搜索支持"""
        # 返回所有记录，因为权限在write方法中控制
        return []

    def write(self, vals):
        """重写write方法，控制价格字段的修改权限"""
        # 需要检查的字段
        price_fields = ['price_unit', 'product_qty', 'discount']
        
        # 检查是否有价格字段需要修改
        if any(field in vals for field in price_fields):
            # 获取当前用户
            current_user = self.env.user
            purchase_group = self.env.ref('purchase.group_purchase_user', False)
            sale_group = self.env.ref('sales_team.group_sale_salesman', False)
            
            is_purchase_user = purchase_group and purchase_group in current_user.groups_id
            is_sale_user = sale_group and sale_group in current_user.groups_id
            
            for order in self:
                # 如果是销售创建的RFQ且当前用户是采购
                if (order.creator_type == 'sale' and is_purchase_user and not is_sale_user):
                    if order.state in ('draft', 'sent'):
                        raise AccessError(
                            _('您不能修改销售创建的RFQ价格。\n'
                              '如需修改，请联系RFQ创建者或销售经理。')
                        )
        
        return super().write(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def write(self, vals):
        """重写write方法，控制价格字段的修改权限"""
        price_fields = ['price_unit', 'product_qty', 'discount']
        
        if any(field in vals for field in price_fields):
            current_user = self.env.user
            purchase_group = self.env.ref('purchase.group_purchase_user', False)
            sale_group = self.env.ref('sales_team.group_sale_salesman', False)
            
            is_purchase_user = purchase_group and purchase_group in current_user.groups_id
            is_sale_user = sale_group and sale_group in current_user.groups_id
            
            for line in self:
                order = line.order_id
                if (order.creator_type == 'sale' and is_purchase_user and not is_sale_user):
                    if order.state in ('draft', 'sent'):
                        raise AccessError(
                            _('您不能修改销售创建的RFQ价格。')
                        )
        
        return super().write(vals)
