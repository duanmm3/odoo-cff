# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    approval_state = fields.Selection([
        ('draft', '草稿'),
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ], '审批状态', default='draft', copy=False)
    
    approval_user_id = fields.Many2one('res.users', '审批人', copy=False)
    approval_date = fields.Datetime('审批时间', copy=False)
    approval_request_id = fields.Many2one('approval.request', '审批请求', copy=False)