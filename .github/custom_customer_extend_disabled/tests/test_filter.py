#!/usr/bin/env python3
"""
测试搜索过滤器
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

# 测试搜索 - 使用过滤器
# 搜索"我的联系人"
partners = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read',
    [('create_uid', '=', uid)], ['name'])
print(f"我的联系人: {len(partners)}")
for p in partners:
    print(f"  - {p['name']}")

# 搜索"共享给我"
shared = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read',
    [('shared_users', 'in', [uid])], ['name'])
print(f"\n共享给我: {len(shared)}")
for p in shared:
    print(f"  - {p['name']}")

# 组合搜索
combined = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read',
    ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])], ['name'])
print(f"\n总计: {len(combined)}")
for p in combined:
    print(f"  - {p['name']}")
