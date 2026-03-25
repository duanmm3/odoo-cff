# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    # 审批相关字段
    approval_state = fields.Selection([
        ('no', '无需审批'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ], '审批状态', default='no', copy=False)
    
    approval_user_id = fields.Many2one('res.users', '审批人', copy=False)
    approval_date = fields.Datetime('审批时间', copy=False)
    
    approval_request_id = fields.Many2one('approval.request', '审批请求', copy=False)
    
    need_approval = fields.Boolean('需要审批', compute='_compute_need_approval', store=True)
    
    @api.depends('amount_total')
    def _compute_need_approval(self):
        """计算是否需要审批"""
        for order in self:
            # 超过1000需要审批
            order.need_approval = order.amount_total > 1000
    
    def button_confirm(self):
        """确认订单时检查是否需要审批"""
        for order in self:
            if order.need_approval and order.approval_state in ['no', False]:
                raise UserError('此采购订单金额超过审批限额，需要采购经理审批通过后才能确认!')
            
            if order.need_approval and order.approval_state == 'rejected':
                raise UserError('此采购订单审批被拒绝，无法确认!')
                
        return super(PurchaseOrder, self).button_confirm()
    
    def action_submit_approval(self):
        """提交审批"""
        self.ensure_one()
        
        if self.approval_state not in ['no', 'rejected']:
            return False
        
        # 创建审批请求
        approval_category = self.env['approval.category'].search([('code', '=', 'purchase_order')], limit=1)
        if not approval_category:
            approval_category = self.env['approval.category'].create({
                'name': '采购订单审批',
                'code': 'purchase_order',
                'description': '采购订单需要采购经理审批',
            })
        
        # 查找采购经理
        approver = self.env['res.users'].search([('groups_id.name', 'ilike', '采购经理')], limit=1)
        if not approver:
            approver = self.env.ref('base.group_purchase_manager').users[:1]
        if not approver:
            approver = self.env.user
        
        approval_request = self.env['approval.request'].create({
            'category_id': approval_category.id,
            'requester_id': self.env.user.id,
            'approver_id': approver.id,
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'note': f'采购订单审批: {self.name}, 金额: {self.amount_total}',
            'purchase_order_id': self.id,
            'company_id': self.company_id.id,
        })
        
        # 提交审批
        approval_request.action_submit()
        
        # 更新采购订单状态
        self.write({
            'approval_request_id': approval_request.id,
            'approval_state': 'pending',
        })
        
        return True
    
    def action_view_approval(self):
        """查看审批请求"""
        self.ensure_one()
        if self.approval_request_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'approval.request',
                'res_id': self.approval_request_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False
