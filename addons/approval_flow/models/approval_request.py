# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ApprovalCategory(models.Model):
    _name = 'approval.category'
    _description = '审批类型'
    _order = 'name'

    name = fields.Char('审批类型名称', required=True)
    code = fields.Char('编码', required=True)
    description = fields.Text('描述')
    model_id = fields.Many2one('ir.model', '关联模型')
    approval_limit = fields.Float('审批金额限制', default=0)
    
    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError('审批类型编码必须唯一!')


class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _description = '审批请求'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('审批单号', required=True, copy=False, readonly=True, index=True)
    
    category_id = fields.Many2one('approval.category', '审批类型', required=True)
    
    requester_id = fields.Many2one('res.users', '申请人', required=True, default=lambda self: self.env.user)
    
    approver_id = fields.Many2one('res.users', '审批人', required=True)
    
    partner_id = fields.Many2one('res.partner', '业务伙伴')
    
    amount = fields.Float('金额')
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ], '状态', default='draft', tracking=True)
    
    note = fields.Text('申请说明')
    
    reject_reason = fields.Text('拒绝原因')
    
    # 关联的业务单据
    sale_order_id = fields.Many2one('sale.order', '销售订单')
    purchase_order_id = fields.Many2one('purchase.order', '采购订单')
    account_move_id = fields.Many2one('account.move', '发票')
    account_payment_id = fields.Many2one('account.payment', '付款')
    
    date_approved = fields.Datetime('批准时间')
    date_rejected = fields.Datetime('拒绝时间')
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_submit(self):
        """提交审批"""
        for record in self:
            if record.state != 'draft':
                continue
            record.write({
                'state': 'pending',
                'name': self.env['ir.sequence'].next_by_code('approval.request') or '/',
            })
            # 发送通知给审批人
            record._send_notification('pending')
        return True

    def action_approve(self):
        """批准审批"""
        for record in self:
            if record.state != 'pending':
                continue
            
            # 检查权限（审批人或管理员可以批准）
            if record.approver_id != self.env.user and not self.env.user.has_group('base.group_system'):
                raise UserError('只有审批人或管理员才能批准此审批请求!')
            
            record.write({
                'state': 'approved',
                'date_approved': datetime.now(),
            })
            
            # 执行批准后的业务动作
            record._execute_approved_action()
            
            # 发送通知给申请人
            record._send_notification('approved')
        return True

    def action_reject(self, reason=False):
        """拒绝审批"""
        for record in self:
            if record.state != 'pending':
                continue
            
            # 检查权限
            if record.approver_id != self.env.user and not self.env.user.has_group('base.group_system'):
                raise UserError('只有审批人才能拒绝此审批请求!')
            
            record.write({
                'state': 'rejected',
                'date_rejected': datetime.now(),
                'reject_reason': reason or '未说明原因',
            })
            
            # 执行拒绝后的业务动作
            record._execute_rejected_action()
            
            # 发送通知给申请人
            record._send_notification('rejected')
        return True

    def action_draft(self):
        """撤回审批"""
        for record in self:
            if record.state not in ['pending']:
                continue
            record.write({'state': 'draft'})
        return True

    def _send_notification(self, action):
        """发送站内通知"""
        self.ensure_one()
        
        # 通过消息子系统发送通知
        if action == 'pending':
            subject = f'新的审批请求: {self.name}'
            message = f'''
            <p>您有一个新的审批请求需要处理</p>
            <p><b>类型:</b> {self.category_id.name}</p>
            <p><b>申请人:</b> {self.requester_id.name}</p>
            <p><b>金额:</b> {self.amount}</p>
            <p><b>说明:</b> {self.note or ""}</p>
            '''
            partner_ids = [self.approver_id.partner_id.id]
        else:
            subject = f'审批结果: {self.name}'
            if action == 'approved':
                message = f'''
                <p>您的审批请求已获批准</p>
                <p><b>审批人:</b> {self.approver_id.name}</p>
                '''
            else:
                message = f'''
                <p>您的审批请求已被拒绝</p>
                <p><b>审批人:</b> {self.approver_id.name}</p>
                <p><b>拒绝原因:</b> {self.reject_reason}</p>
                '''
            partner_ids = [self.requester_id.partner_id.id]
        
        self.message_post(
            body=message,
            subject=subject,
            partner_ids=partner_ids,
            subtype_xmlid='mail.mt_comment',
        )
        
        # 创建活动提醒
        if action == 'pending':
            self.activity_schedule(
                'approval_flow.mail_act_approval',
                user_id=self.approver_id.id,
                note=message,
            )

    def _execute_approved_action(self):
        """执行批准后的业务动作"""
        self.ensure_one()
        
        # 销售订单审批通过
        if self.sale_order_id:
            # 调用销售订单的审批通过回调方法
            self.sale_order_id.on_approval_approved(self.approver_id)
            # 确认销售订单
            if self.sale_order_id.state == 'draft':
                self.sale_order_id.action_confirm()
        
        # 采购订单审批通过
        if self.purchase_order_id:
            self.purchase_order_id.write({
                'approval_state': 'approved',
                'approval_user_id': self.approver_id.id,
                'approval_date': datetime.now(),
            })
            # 确认采购订单
            if self.purchase_order_id.state == 'draft':
                self.purchase_order_id.button_confirm()
        
        # 发票审批通过
        if self.account_move_id:
            self.account_move_id.sudo().write({
                'approval_state': 'approved',
                'approval_user_id': self.approver_id.id,
                'approval_date': datetime.now(),
            })
        
        # 付款审批通过
        if self.account_payment_id:
            self.account_payment_id.sudo().write({
                'approval_state': 'approved',
                'approval_user_id': self.approver_id.id,
                'approval_date': datetime.now(),
            })

    def _execute_rejected_action(self):
        """执行拒绝后的业务动作"""
        self.ensure_one()
        
        # 销售订单审批拒绝
        if self.sale_order_id:
            # 调用销售订单的审批拒绝回调方法
            self.sale_order_id.on_approval_rejected(self.approver_id, self.reject_reason or '')
        
        # 采购订单审批拒绝
        if self.purchase_order_id:
            self.purchase_order_id.write({
                'approval_state': 'rejected',
            })
        
        # 发票审批拒绝
        if self.account_move_id:
            self.account_move_id.write({
                'approval_state': 'rejected',
            })
        
        # 付款审批拒绝
        if self.account_payment_id:
            self.account_payment_id.write({
                'approval_state': 'rejected',
            })
