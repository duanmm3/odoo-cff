# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
完整版: 带审批工作流的RFQ价格控制
"""

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.addons.sale.models.sale_order import SaleOrder


class PurchaseOrderApproval(models.Model):
    """RFQ价格修改审批"""
    _name = 'purchase.rfq.price.approval'
    _description = 'RFQ价格修改审批'
    _order = 'create_date desc'

    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        required=True,
        ondelete='cascade'
    )
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        required=True,
        default=lambda self: self.env.user
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True
    )
    state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending', string='Status')

    original_price = fields.Float(string='Original Price')
    new_price = fields.Float(string='New Price')
    reason = fields.Text(string='Reason for Change')

    def approve(self):
        """批准价格修改"""
        for approval in self:
            approval.write({
                'approved_by': self.env.user.id,
                'state': 'approved'
            })
        return True

    def reject(self):
        """拒绝价格修改"""
        for approval in self:
            approval.write({
                'approved_by': self.env.user.id,
                'state': 'rejected'
            })
        return True


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # 价格修改审批状态
    price_approval_state = fields.Selection([
        ('none', 'No Approval Needed'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
    ], default='none', string='Price Approval Status', compute='_compute_price_approval_state')

    pending_approval_ids = fields.One2many(
fq.price.approval',
        'order        'purchase.r_id',
        string='Pending Approvals',
        domain=[('state', '=', 'pending')]
    )

    @api.depends('pending_approval_ids', 'pending_approval_ids.state')
    def _compute_price_approval_state(self):
        """计算审批状态"""
        for order in self:
            if order.pending_approval_ids:
                order.price_approval_state = 'pending'
            else:
                order.price_approval_state = 'none'

    def request_price_change(self, new_price, reason):
        """申请价格修改"""
        self.ensure_one()
        
        # 检查是否需要审批
        if not self.is_from_sale:
            # 非销售来源，直接修改
            self.write({'price_unit': new_price})
            return True
        
        # 销售来源需要审批
        # 检查是否有待审批
        if self.pending_approval_ids:
            raise UserError(_('已有待审批的价格修改请求'))
        
        # 创建审批请求
        approval = self.env['purchase.rfq.price.approval'].create({
            'order_id': self.id,
            'original_price': self.price_unit,
            'new_price': new_price,
            'reason': reason,
        })
        
        # 发送通知给销售经理
        self._send_approval_notification()
        
        return True

    def _send_approval_notification(self):
        """发送审批通知"""
        # 获取销售经理
        sale_manager_group = self.env.ref('sales_team.group_sale_manager')
        if not sale_manager_group:
            return
        
        # 通知消息
        self.message_post(
            body=_('有新的RFQ价格修改等待审批'),
            subject=_('RFQ价格修改审批'),
            partner_ids=sale_manager_group.users.mapped('partner_id.id')
        )

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
                # 来自销售的RFQ，需要审批才能修改
                if (order.is_from_sale and is_purchase_user and not is_sale_user):
                    if order.state in ('draft', 'sent'):
                        # 已经有批准的审批单
                        approved = order.pending_approval_ids.filtered(
                            lambda a: a.state == 'approved' and 
                            a.new_price == vals.get('price_unit')
                        )
                        if not approved:
                            raise AccessError(
                                _('此询价单来自销售，需要销售经理审批后才能修改价格。\n'
                                  '请使用"申请价格修改"功能。')
                            )
        
        return super().write(vals)

    def action_request_price_change(self):
        """打开价格修改申请向导"""
        return {
            'name': _('Request Price Change'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.rfq.price.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }
