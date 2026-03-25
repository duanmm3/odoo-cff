#!/usr/bin/env python3
"""
找到并禁用所有有问题的自定义视图
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 查找所有继承 res.partner 的自定义视图
views = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
    [('model', '=', 'res.partner'), ('type', '=', 'list')],
    ['id', 'name', 'inherit_id', 'active'])

print("=== res.partner list 视图 ===")
for v in views:
    print(f"ID: {v['id']}, Name: {v['name']}, Active: {v['active']}, Inherit: {v['inherit_id']}")
