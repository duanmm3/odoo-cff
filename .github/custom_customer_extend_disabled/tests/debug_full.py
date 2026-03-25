#!/usr/bin/env python3
"""
模拟页面加载 - 检查所有需要的权限
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# 用 Amanda 登录
uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

print(f"Amanda UID: {uid}")

# 测试各种模型访问
models_to_test = [
    'res.partner',
    'ir.actions.act_window', 
    'ir.ui.menu',
    'ir.ui.view',
    'ir.model.data',
]

for model in models_to_test:
    try:
        result = models.execute('app', uid, 'Odoo123456', model, 'search_count', [])
        print(f"✓ {model}: {result} 条")
    except Exception as e:
        print(f"✗ {model}: {str(e)[:60]}")
