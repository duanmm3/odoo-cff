#!/usr/bin/env python3
"""
禁用有问题的自定义视图
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 禁用视图
models.execute('app', uid, 'admin', 'ir.ui.view', 'write', [1151], {
    'active': False
})
print("✓ 已禁用视图 1151")

# 刷新缓存
models.execute_kw('app', uid, 'admin', 'ir.ui.view', 'invalidate_cache', [[]])
print("✓ 已刷新缓存")
