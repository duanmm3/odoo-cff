# -*- coding: utf-8 -*-
{
    'name': 'AI Report (Chat2BI)',
    'version': '3.0.0',
    'category': 'Reporting',
    'summary': 'Natural Language to BI — WrenAI Embedded',
    'description': """
AI Report 模块将 WrenAI 语义层能力嵌入 Odoo 19，
实现自然语言查询业务数据、数据可视化、DML 操作。
支持基于角色的权限控制（销售/采购/仓库/管理员）。
    """,
    'author': 'AI Report Development Team',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'purchase', 'stock', 'web'],
    'external_dependencies': {
        'python': ['pyyaml', 'requests'],
    },
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/ai_report_settings_views.xml',  # 先加载 action 定义
        'views/ai_report_menus.xml',         # 后加载 menu
        'views/ai_report_chat_views.xml',
        'views/ai_report_audit_views.xml',
        'views/ai_report_web.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ai_report/static/src/css/ai_report.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}