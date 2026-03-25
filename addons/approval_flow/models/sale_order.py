# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
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
    
    need_approval = fields.Boolean('需要审批', compute='_compute_need_approval', store=False)
    
    @api.depends('amount_total')
    def _compute_need_approval(self):
        """计算是否需要审批"""
        for order in self:
            # 超过1000需要审批，可配置
            order.need_approval = order.amount_total > 1000
    
    def action_confirm(self):
        """确认订单时检查是否需要审批"""
        for order in self:
            if order.need_approval and order.approval_state in ['no', False]:
                # 需要审批但未审批，禁止确认
                raise UserError('此销售订单金额超过审批限额，需要销售经理审批通过后才能确认!')
            
            if order.need_approval and order.approval_state == 'rejected':
                raise UserError('此销售订单审批被拒绝，无法确认!')
                
        return super(SaleOrder, self).action_confirm()
    
    def action_submit_approval(self):
        """提交审批"""
        self.ensure_one()
        
        if self.approval_state not in ['no', 'rejected']:
            raise UserError('当前状态不能提交审批！')
        
        # 创建审批请求
        approval_category = self.env['approval.category'].search([('code', '=', 'sale_order')], limit=1)
        if not approval_category:
            approval_category = self.env['approval.category'].create({
                'name': '销售订单审批',
                'code': 'sale_order',
                'description': '销售订单需要销售经理审批',
            })
        
        # 查找销售经理
        approver = self.env['res.users'].search([('groups_id.name', 'ilike', '销售经理')], limit=1)
        if not approver:
            approver = self.env.ref('base.group_sales_manager').users[:1]
        if not approver:
            approver = self.env.user
        
        approval_request = self.env['approval.request'].create({
            'category_id': approval_category.id,
            'requester_id': self.env.user.id,
            'approver_id': approver.id,
            'partner_id': self.partner_id.id,
            'amount': self.amount_total,
            'note': f'销售订单审批: {self.name}, 客户: {self.partner_id.name}, 金额: {self.amount_total}',
            'sale_order_id': self.id,
            'company_id': self.company_id.id,
        })
        
        # 提交审批
        approval_request.action_submit()
        
        # 更新销售订单状态
        self.write({
            'approval_request_id': approval_request.id,
            'approval_state': 'pending',
        })
        
        # 发送通知
        self._send_approval_notification(approver)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'res_id': approval_request.id,
            'view_mode': 'form',
            'target': 'current',
            'flags': {'form': {'action_buttons': True}},
        }
    
    def _send_approval_notification(self, approver):
        """发送审批通知"""
        body = f"""
        <p>您有一个新的销售订单需要审批：</p>
        <ul>
            <li>订单编号: {self.name}</li>
            <li>客户: {self.partner_id.name}</li>
            <li>金额: {self.amount_total}</li>
            <li>申请人: {self.env.user.name}</li>
        </ul>
        <p>请及时处理。</p>
        """
        
        self.message_post(
            body=body,
            partner_ids=[approver.partner_id.id],
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )
    
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
                'flags': {'form': {'action_buttons': True}},
            }
        return False
    
    def on_approval_approved(self, approver):
        """审批通过时的回调"""
        self.ensure_one()
        self.write({
            'approval_state': 'approved',
            'approval_user_id': approver.id,
            'approval_date': fields.Datetime.now(),
        })
        
        # 发送通知
        body = f"""
        <p>销售订单审批已通过：</p>
        <ul>
            <li>订单编号: {self.name}</li>
            <li>客户: {self.partner_id.name}</li>
            <li>金额: {self.amount_total}</li>
            <li>审批人: {approver.name}</li>
            <li>审批时间: {fields.Datetime.now()}</li>
        </ul>
        """
        
        self.message_post(
            body=body,
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )
        
        return True
    
    def on_approval_rejected(self, approver, reason=''):
        """审批拒绝时的回调"""
        self.ensure_one()
        self.write({
            'approval_state': 'rejected',
            'approval_user_id': approver.id,
            'approval_date': fields.Datetime.now(),
        })
        
        # 发送通知
        body = f"""
        <p>销售订单审批被拒绝：</p>
        <ul>
            <li>订单编号: {self.name}</li>
            <li>客户: {self.partner_id.name}</li>
            <li>金额: {self.amount_total}</li>
            <li>审批人: {approver.name}</li>
            <li>拒绝原因: {reason}</li>
            <li>审批时间: {fields.Datetime.now()}</li>
        </ul>
        """
        
        self.message_post(
            body=body,
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )
        
        return True
