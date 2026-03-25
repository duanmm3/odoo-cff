#!/usr/bin/env python3
"""
检查列表视图
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 查找自定义列表视图
views = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
    [('model', '=', 'res.partner'), ('type', '=', 'list'), ('name', 'like', 'custom')],
    ['id', 'name', 'inherit_id', 'active'])

print("=== 自定义列表视图 ===")
for v in views:
    print(f"ID: {v['id']}, Name: {v['name']}, Active: {v['active']}, Inherit: {v['inherit_id']}")

# 检查基础视图
base_view = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
    [('id', '=', 124)],
    ['id', 'name', 'arch_db'])
    
print("\n=== 基础视图 (ID 124) ===")
if base_view:
    print(f"Name: {base_view[0]['name']}")
