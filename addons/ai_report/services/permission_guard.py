# -*- coding: utf-8 -*-
"""Permission Guard — 权限守卫"""

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class PermissionGuard(models.AbstractModel):
    _name = 'ai.report.permission'
    _description = 'AI Report 权限守卫'

    ROLE_MODEL_MAP = {
        'sales': ['sale_order', 'sale_order_line', 'product_product', 'product_template', 'res_partner'],
        'purchase': ['purchase_order', 'purchase_order_line', 'product_product', 'product_template', 'res_partner'],
        'warehouse': ['stock_move', 'stock_picking', 'stock_quant', 'product_product', 'product_template'],
        'admin': None,
    }

    ROLE_DML_MAP = {
        'sales': ['sale_create', 'sale_update', 'sale_delete'],
        'purchase': ['purchase_create', 'purchase_update', 'purchase_delete'],
        'warehouse': ['stock_in', 'stock_out'],
        'admin': None,
    }

    @api.model
    def get_user_role(self) -> str:
        """获取当前用户的 AI Report 角色"""
        user = self.env.user
        if user.has_group('base.group_system') or user.has_group('ai_report.group_ai_report_manager'):
            return 'admin'
        if user.has_group('ai_report.group_sales_analyst'):
            return 'sales'
        if user.has_group('ai_report.group_purchase_analyst'):
            return 'purchase'
        if user.has_group('ai_report.group_warehouse_analyst'):
            return 'warehouse'
        return 'admin'

    @api.model
    def check_query_permission(self, role: str, question: str) -> dict:
        """检查查询权限"""
        module_keywords = {
            'sales': ['销售', '订单', '客户', '销售额', '畅销', 'sale', 'revenue', 'customer'],
            'purchase': ['采购', '供应商', '进货', 'purchase', 'supplier', 'vendor'],
            'warehouse': ['库存', '入库', '出库', '仓', 'stock', 'inventory', 'warehouse'],
        }

        involved_modules = set()
        for module, keywords in module_keywords.items():
            for kw in keywords:
                if kw.lower() in question.lower():
                    involved_modules.add(module)
                    break

        if not involved_modules:
            return {'allowed': True, 'reason': ''}

        allowed_models = self.ROLE_MODEL_MAP.get(role)
        if allowed_models is None:
            return {'allowed': True, 'reason': ''}

        module_to_models = {
            'sales': ['sale_order', 'sale_order_line'],
            'purchase': ['purchase_order', 'purchase_order_line'],
            'warehouse': ['stock_move', 'stock_picking', 'stock_quant'],
        }

        for module in involved_modules:
            models_needed = module_to_models.get(module, [])
            for model in models_needed:
                if model not in allowed_models:
                    return {'allowed': False, 'reason': f'您的角色无权访问该模块数据'}

        return {'allowed': True, 'reason': ''}

    @api.model
    def check_dml_permission(self, role: str, intent: str) -> dict:
        """检查 DML 操作权限"""
        allowed_intents = self.ROLE_DML_MAP.get(role)
        if allowed_intents is None:
            return {'allowed': True, 'reason': '', 'need_approval': False}

        if intent not in allowed_intents:
            return {'allowed': False, 'reason': f'您的角色无权执行此操作', 'need_approval': False}

        return {'allowed': True, 'reason': '', 'need_approval': False}