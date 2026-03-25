#!/usr/bin/env python3
"""
检查自定义 action
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查自定义 action
actions = models.execute('app', uid, 'admin', 'ir.actions.act_window', 'search_read',
    [('name', '=', 'Contacts'), ('id', '>', 300)],
    ['id', 'name', 'res_model', 'context', 'domain'])

print("=== 自定义 Contacts Action ===")
for a in actions:
    print(f"ID: {a['id']}, Name: {a['name']}")
    print(f"Context: {a.get('context')}")
    print(f"Domain: {a.get('domain')}")
