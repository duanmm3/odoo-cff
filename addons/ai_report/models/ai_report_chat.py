# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)


class AiReportChat(models.Model):
    _name = 'ai.report.chat'
    _description = 'AI Report 对话记录'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', '用户', required=True)
    session_id = fields.Char('会话ID', required=True, index=True)
    role = fields.Char('用户角色')
    message_type = fields.Selection([
        ('user', '用户消息'),
        ('assistant', '助手回复'),
    ], '消息类型')
    content = fields.Text('消息内容')
    result_type = fields.Selection([
        ('query', '查询结果'),
        ('dml', '操作结果'),
        ('error', '错误'),
        ('info', '提示'),
    ], '结果类型')
    result_json = fields.Text('结果数据 JSON')
    sql_generated = fields.Text('生成的 SQL')
    chart_type = fields.Char('图表类型')
    execution_time = fields.Float('执行时间(秒)')
    create_date = fields.Datetime('创建时间')

    @api.model
    def save_chat(self, session_id, message_type, content, result_type='info', result=None, sql=None, chart_type=None):
        """保存对话记录"""
        try:
            role = 'admin'
            try:
                permission_model = self.env['ai.report.permission']
                if hasattr(permission_model, 'get_user_role'):
                    role = permission_model.get_user_role()
            except Exception:
                role = 'admin'

            user_id = self.env.uid or self.env.ref('base.user_root').id
            
            vals = {
                'user_id': user_id,
                'session_id': session_id,
                'role': role,
                'message_type': message_type,
                'content': content,
                'result_type': result_type,
            }
            if result is not None:
                vals['result_json'] = json.dumps(result, ensure_ascii=False)
            if sql:
                vals['sql_generated'] = sql
            if chart_type:
                vals['chart_type'] = chart_type
            return self.create(vals)
        except Exception as e:
            _logger = logging.getLogger(__name__)
            _logger.error(f"save_chat error: {e}")
            return False

    @api.model
    def get_session_history(self, session_id):
        return self.search([('session_id', '=', session_id)], order='create_date asc')
