# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
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
        for order in self:
            order.need_approval = order.amount_total > 1000
    
    def button_confirm(self):
        return super(PurchaseOrder, self).button_confirm()
    
    def action_submit_approval(self):
        for rec in self:
            rec_id = rec.id
            
            self.env.cr.execute("SELECT approval_state FROM purchase_order WHERE id = %s", (rec_id,))
            result = self.env.cr.fetchone()
            state = result[0] if result else None
            
            if state and state not in ['no', 'rejected']:
                raise UserError('当前状态不能提交审批!')
            
            self.env.cr.execute("SELECT partner_id, amount_total, name, company_id FROM purchase_order WHERE id = %s", (rec_id,))
            move_data = self.env.cr.fetchone()
            if not move_data:
                raise UserError('订单不存在!')
            partner_id, amount_total, move_name, company_id = move_data
            
            partner_name = ''
            if partner_id:
                self.env.cr.execute("SELECT name FROM res_partner WHERE id = %s", (partner_id,))
                partner_result = self.env.cr.fetchone()
                partner_name = partner_result[0] if partner_result else ''
            
            self.env.cr.execute("SELECT id FROM approval_category WHERE code = 'purchase_order' LIMIT 1")
            cat_result = self.env.cr.fetchone()
            if cat_result:
                approval_category_id = cat_result[0]
            else:
                self.env.cr.execute("INSERT INTO approval_category (name, code, description) VALUES ('采购订单审批', 'purchase_order', '采购订单需要采购经理审批') RETURNING id")
                approval_category_id = self.env.cr.fetchone()[0]
            
            self.env.cr.execute("SELECT u.id FROM res_users u JOIN res_groups_users_rel gu ON u.id = gu.uid JOIN res_groups g ON gu.gid = g.id WHERE g.name::text LIKE '%Purchase Manager%' LIMIT 1")
            user_result = self.env.cr.fetchone()
            approver_id = user_result[0] if user_result else self.env.user.id
            
            import time
            seq_num = int(time.time() * 1000) % 1000000
            approval_name = f'{partner_name or "未知"}/{datetime.now().strftime("%Y%m%d")}/{seq_num}'
            
            self.env.cr.execute("INSERT INTO approval_request (name, category_id, requester_id, approver_id, partner_id, amount, note, purchase_order_id, company_id, state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending') RETURNING id",
                (approval_name, approval_category_id, self.env.user.id, approver_id, partner_id, amount_total, f'采购订单审批: {move_name}, 金额: {amount_total}', rec_id, company_id))
            approval_request_id = self.env.cr.fetchone()[0]
            
            self.env.cr.execute("UPDATE purchase_order SET approval_state = 'pending', approval_request_id = %s WHERE id = %s", (approval_request_id, rec_id))
            
            self.env.cr.execute(
                "SELECT requester_id, approver_id, category_id, amount, note FROM approval_request WHERE id = %s",
                (approval_request_id,)
            )
            req_data = self.env.cr.fetchone()
            if req_data:
                requester_id, approver_id, category_id, amount, note = req_data
                self.env.cr.execute("SELECT partner_id FROM res_users WHERE id = %s", (approver_id,))
                approver = self.env.cr.fetchone()
                if approver:
                    self.env.cr.execute("""
                        INSERT INTO mail_message (create_uid, body, subject, model, res_id, message_type)
                        VALUES (%s, %s, %s, 'approval.request', %s, 'comment')
                        RETURNING id
                    """, (self.env.user.id, f'<p>您有一个新的审批请求需要处理</p><p><b>类型:</b> 采购订单审批</p><p><b>金额:</b> {amount}</p><p><b>说明:</b> {note or ""}</p>', f'新的审批请求: {approval_name}', approval_request_id))
                    msg_id = self.env.cr.fetchone()[0]
                    self.env.cr.execute("""
                        INSERT INTO mail_notification (mail_message_id, res_partner_id, notification_type, is_read)
                        VALUES (%s, %s, 'inbox', false)
                    """, (msg_id, approver[0]))
        
        return True
    
    def action_view_approval(self):
        self.ensure_one()
        if self.approval_request_id:
            return {'type': 'ir.actions.act_window', 'res_model': 'approval.request', 'res_id': self.approval_request_id.id, 'view_mode': 'form', 'target': 'current'}
        return False