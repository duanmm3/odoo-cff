#!/usr/bin/env python3
"""
检查自定义视图的 arch
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 读取自定义视图
view = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
    [('id', '=', 1151)],
    ['arch_db'])

print("=== 自定义视图 arch ===")
if view:
    print(view[0]['arch_db'])
