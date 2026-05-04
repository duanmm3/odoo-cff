# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AiReportSettings(models.Model):
    _name = 'ai.report.settings'
    _description = 'AI Report 全局设置'

    name = fields.Char('设置名称', default='AI Report Configuration')
    enable_dml = fields.Boolean('启用DML操作', default=True)
    dml_require_approval = fields.Boolean('DML需要审批', default=False)
    approval_threshold_amount = fields.Float('审批金额阈值', default=50000)
    max_query_rows = fields.Integer('最大返回行数', default=1000)
    query_timeout = fields.Integer('查询超时(秒)', default=30)
    llm_api_base = fields.Char('LLM API地址', default='https://genuine-applicants-templates-differ.trycloudflare.com/v1')
    llm_model = fields.Char('LLM模型', default='local-model')
    sales_can_query = fields.Boolean('销售可查询', default=True)
    sales_can_create = fields.Boolean('销售可创建', default=True)
    sales_can_delete = fields.Boolean('销售可删除', default=True)
    purchase_can_query = fields.Boolean('采购可查询', default=True)
    purchase_can_create = fields.Boolean('采购可创建', default=True)
    purchase_can_delete = fields.Boolean('采购可删除', default=True)
    warehouse_can_query = fields.Boolean('仓库可查询', default=True)
    warehouse_can_stock_in = fields.Boolean('仓库可入库', default=True)
    warehouse_can_stock_out = fields.Boolean('仓库可出库', default=True)
    enable_row_level_security = fields.Boolean('启用行级安全', default=True)
    sales_see_own_only = fields.Boolean('销售仅看自己的', default=False)
    purchase_see_own_only = fields.Boolean('采购仅看自己的', default=False)

    @api.model
    def get_settings(self):
        """获取全局设置"""
        settings = self.search([], limit=1)
        if not settings:
            settings = self.create({})
        return settings

    @api.model
    def get_param(self, key, default=None):
        """获取配置参数"""
        param = self.env['ir.config_parameter'].sudo().search([
            ('key', '=', f'ai_report.{key}')
        ], limit=1)
        return param.value if param else default