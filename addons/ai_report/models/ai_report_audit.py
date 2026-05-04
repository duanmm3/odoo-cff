# -*- coding: utf-8 -*-
from odoo import models, fields


class AiReportAudit(models.Model):
    _name = 'ai.report.audit'
    _description = 'AI Report 操作审计日志'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', '操作用户')
    user_role = fields.Char('用户角色')
    action_type = fields.Selection([
        ('query', '数据查询'),
        ('sale_create', '创建销售订单'),
        ('sale_update', '修改销售订单'),
        ('sale_delete', '删除销售订单'),
        ('purchase_create', '创建采购订单'),
        ('purchase_update', '修改采购订单'),
        ('purchase_delete', '删除采购订单'),
        ('stock_in', '入库'),
        ('stock_out', '出库'),
    ], '操作类型')
    question = fields.Text('原始问题')
    generated_sql = fields.Text('生成的 SQL')
    result_summary = fields.Text('结果摘要')
    status = fields.Selection([
        ('success', '成功'),
        ('failed', '失败'),
        ('denied', '权限拒绝'),
    ], '状态')
    error_message = fields.Text('错误信息')
    execution_time = fields.Float('执行时间(秒)')
    create_date = fields.Datetime('操作时间')