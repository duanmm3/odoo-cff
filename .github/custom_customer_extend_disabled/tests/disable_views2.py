#!/usr/bin/env python3
"""
禁用有问题的视图
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 禁用视图 1151 和 1153
for view_id in [1151, 1153]:
    try:
        models.execute('app', uid, 'admin', 'ir.ui.view', 'write', [view_id], {'active': False})
        print(f"✓ 已禁用视图 {view_id}")
    except Exception as e:
        print(f"✗ 视图 {view_id}: {e}")

print("\n完成!")
