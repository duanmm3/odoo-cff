#!/usr/bin/env python3
"""
检查自定义视图是否正确
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查自定义列表视图
view = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
    [('id', '=', 1151)],
    ['arch_db', 'active'])

print("=== 自定义列表视图 ===")
if view:
    print(f"Active: {view[0]['active']}")
    print(f"Arch: {view[0]['arch_db']}")
