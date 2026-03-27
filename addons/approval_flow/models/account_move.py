# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    approval_state = fields.Selection([
        ('draft', '草稿'),
        ('pending', '待审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ], '审批状态', default='draft', copy=False)
    
    approval_user_id = fields.Many2one('res.users', '审批人', copy=False)
    approval_date = fields.Datetime('审批时间', copy=False)
    
    approval_request_id = fields.Many2one('approval.request', '审批请求', copy=False)
    
    need_approval = fields.Boolean('需要审批', compute='_compute_need_approval', store=True)
    
    @api.depends('amount_total')
    def _compute_need_approval(self):
        limit = float(self.env['ir.config_parameter'].sudo().get_param('approval_flow.invoice_limit', '5000'))
        for move in self:
            move.need_approval = move.approval_state == 'draft' and move.amount_total > limit
    
    def _get_invoice_limit(self):
        return float(self.env['ir.config_parameter'].sudo().get_param('approval_flow.invoice_limit', '5000'))
    
    def action_post(self):
        limit = self._get_invoice_limit()
        for move in self:
            if move.move_type in ['out_invoice', 'in_invoice']:
                if move.approval_state == 'pending':
                    raise UserError('该发票待审批通过后才能确认。')
                if move.amount_total > limit and move.approval_state == 'draft':
                    move._create_approval_request()
        return super(AccountMove, self).action_post()
    
    def _create_approval_request(self):
        """自动创建审批请求"""
        self.ensure_one()
        rec_id = self.id
        
        partner_name = self.partner_id.name if self.partner_id else ''
        
        self.env.cr.execute(
            "SELECT id FROM approval_category WHERE code = 'invoice_payment' LIMIT 1"
        )
        cat_result = self.env.cr.fetchone()
        if cat_result:
            approval_category_id = cat_result[0]
        else:
            self.env.cr.execute(
                "INSERT INTO approval_category (name, code, description) VALUES ('发票审批', 'invoice_payment', '发票需要审批') RETURNING id"
            )
            approval_category_id = self.env.cr.fetchone()[0]
        
        self.env.cr.execute(
            "SELECT u.id FROM res_users u JOIN res_groups_users_rel gu ON u.id = gu.uid "
            "JOIN res_groups g ON gu.gid = g.id WHERE g.name::text LIKE '%Account%' OR g.name::text LIKE '%财务%' LIMIT 1"
        )
        user_result = self.env.cr.fetchone()
        if user_result:
            approver_id = user_result[0]
        else:
            self.env.cr.execute("SELECT id FROM res_users WHERE login = 'admin' LIMIT 1")
            admin_result = self.env.cr.fetchone()
            approver_id = admin_result[0] if admin_result else self.env.user.id
        
        import time
        seq_num = int(time.time() * 1000) % 1000000
        approval_name = f'{partner_name or "未知"}/{datetime.now().strftime("%Y%m%d")}/{seq_num}'
        
        self.env.cr.execute(
            "INSERT INTO approval_request (name, category_id, requester_id, approver_id, partner_id, amount, note, account_move_id, company_id, state) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending') RETURNING id",
            (approval_name, approval_category_id, self.env.user.id, approver_id, self.partner_id.id, self.amount_total,
             f'发票审批: {self.name}, 金额: {self.amount_total}', rec_id, self.company_id.id)
        )
        approval_request_id = self.env.cr.fetchone()[0]
        
        self.env.cr.execute(
            "UPDATE account_move SET approval_state = 'pending', approval_request_id = %s WHERE id = %s",
            (approval_request_id, rec_id)
        )
        
        self.env.cr.execute("SELECT partner_id FROM res_users WHERE id = %s", (approver_id,))
        approver = self.env.cr.fetchone()
        if approver:
            self.env.cr.execute("""
                INSERT INTO mail_message (create_uid, body, subject, model, res_id, message_type)
                VALUES (%s, %s, %s, 'approval.request', %s, 'comment')
                RETURNING id
            """, (self.env.user.id, f'<p>您有一个新的审批请求</p><p><b>类型:</b> 发票审批</p><p><b>金额:</b> {self.amount_total}</p>', f'审批请求: {approval_name}', approval_request_id))
            msg_id = self.env.cr.fetchone()[0]
            self.env.cr.execute("""
                INSERT INTO mail_notification (mail_message_id, res_partner_id, notification_type, is_read)
                VALUES (%s, %s, 'inbox', false)
            """, (msg_id, approver[0]))
        
        _logger.info(f"自动创建审批请求: {approval_name} for invoice {self.name}")
        return True
    
    def action_register_payment(self):
        self.ensure_one()
        if self.approval_state == 'pending':
            raise UserError('该发票待审批通过后才能支付。')
        if self.state != 'posted':
            raise UserError('发票已过账后才能支付。')
        return super(AccountMove, self).action_register_payment()
    
    def action_view_approval(self):
        self.ensure_one()
        if self.approval_request_id:
            return {'type': 'ir.actions.act_window', 'res_model': 'approval.request', 'res_id': self.approval_request_id.id, 'view_mode': 'form', 'target': 'current'}
        return False
    
    def action_approve_invoice(self):
        self.ensure_one()
        if not self.approval_request_id:
            return False
        self.approval_request_id.action_approve()
        return True