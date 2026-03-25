#!/usr/bin/env python3
"""
删除有问题的自定义视图
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 删除自定义视图
views = models.execute('app', uid, 'admin', 'ir.ui.view', 'search',
    [('id', '=', 1151)])

if views:
    models.execute('app', uid, 'admin', 'ir.ui.view', 'unlink', views)
    print(f"✓ 已删除视图: {views}")
else:
    print("未找到视图")

# 刷新缓存
models.execute('app', uid, 'admin', 'ir.ui.view', 'invalidate_cache', [])
print("✓ 已刷新缓存")
