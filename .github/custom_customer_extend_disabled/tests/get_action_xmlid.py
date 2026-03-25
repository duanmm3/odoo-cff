#!/usr/bin/env python3
"""
获取正确的 action external ID
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 查找 action 的 external ID
data = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('model', '=', 'ir.actions.act_window'), ('res_id', '=', 143)],
    ['module', 'name'])

print("=== Action 143 的 External ID ===")
for d in data:
    print(f"{d['module']}.{d['name']}")
