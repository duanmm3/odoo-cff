# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    
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
        for move in self:
            # 发票金额超过1000需要审批（仅对已过账的发票）
            move.need_approval = move.state == 'posted' and move.amount_total > 1000
    
    def action_post(self):
        """过账时检查是否需要审批"""
        for move in self:
            if move.need_approval and move.approval_state in ['no', False]:
                raise UserError('此发票金额超过审批限额，需要财务经理审批通过后才能过账!')
            
            if move.need_approval and move.approval_state == 'rejected':
                raise UserError('此发票审批被拒绝，无法过账!')
                
        return super(AccountMove, self).action_post()
    
    def action_submit_approval(self):
        """提交审批"""
        self.ensure_one()
        
        if self.approval_state not in ['no', 'rejected']:
            return False
        
        # 创建审批请求
        approval_category = self.env['approval.category'].search([('code', '=', 'invoice_payment')], limit=1)
        if not approval_category:
            approval_category = self.env['approval.category'].create({
                'name': '发票支付审批',
                'code': 'invoice_payment',
                'description': '发票支付需要财务经理审批',
            })
        
        # 查找财务经理
        approver = self.env['res.users'].search([('groups_id.name', 'ilike', '财务经理')], limit=1)
        if not approver:
            approver = self.env.ref('account.group_account_manager').users[:1]
        if not approver:
            approver = self.env.user
        
        approval_request = self.env['approval.request'].create({
            'category_id': approval_category.id,
            'requester_id': self.env.user.id,
            'approver_id': approver.id,
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'note': f'发票支付审批: {self.name}, 金额: {self.amount_total}',
            'account_move_id': self.id,
            'company_id': self.company_id.id,
        })
        
        # 提交审批
        approval_request.action_submit()
        
        # 更新发票状态
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
