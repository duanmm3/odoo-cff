#!/usr/bin/env python3
"""
测试带过滤器的搜索
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

# 用过滤器搜索 - create_uid
partners = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', 
    [('create_uid', '=', uid)], ['name'])
print(f"我创建的: {len(partners)}")
for p in partners:
    print(f"  - {p['name']}")

# 用过滤器搜索 - shared_users
shared = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', 
    [('shared_users', 'in', [uid])], ['name'])
print(f"\n共享给我: {len(shared)}")
for p in shared:
    print(f"  - {p['name']}")

# 组合
all_filtered = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', 
    ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])], ['name'])
print(f"\n组合: {len(all_filtered)}")
for p in all_filtered:
    print(f"  - {p['name']}")
