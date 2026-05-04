# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """模块安装后初始化"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("ai_report: 模块已安装")

    try:
        env['ir.config_parameter'].sudo().set_param(
            'ai_report.mdl_initialized', 'true'
        )
        env['ir.config_parameter'].sudo().set_param(
            'ai_report.mdl_version', '3.0'
        )
        env['ir.config_parameter'].sudo().set_param(
            'ai_report.llm_api_base',
            'https://genuine-applicants-templates-differ.trycloudflare.com/v1'
        )
    except Exception as e:
        _logger.warning(f"ai_report: 配置初始化跳过 ({e})")


def uninstall_hook(cr, registry):
    """模块卸载时清理"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env['ir.config_parameter'].sudo().search([
            ('key', 'like', 'ai_report.%')
        ]).unlink()
    except:
        pass