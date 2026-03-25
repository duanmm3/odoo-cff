#!/usr/bin/env python3
"""
检查视图加载问题
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

# 测试直接搜索联系人
partners = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', 
    [], ['name', 'email'], 0, 10)
print(f"联系人数量: {len(partners)}")
for p in partners:
    print(f"  - {p['name']}")

# 测试搜索视图
views = models.execute('app', uid, 'Odoo123456', 'ir.ui.view', 'search_read',
    [('model', '=', 'res.partner'), ('type', '=', 'search')],
    ['name', 'id'])
print(f"\n搜索视图: {len(views)}")
for v in views[:5]:
    print(f"  - {v['name']} (ID: {v['id']})")
