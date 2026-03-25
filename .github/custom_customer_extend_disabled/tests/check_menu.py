#!/usr/bin/env python3
"""
检查菜单配置
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查联系人菜单
menus = models.execute('app', uid, 'admin', 'ir.ui.menu', 'search_read',
    [('name', 'ilike', 'Contact')],
    ['id', 'name', 'action'])

print("=== 联系人菜单 ===")
for m in menus:
    print(f"ID: {m['id']}, Name: {m['name']}, Action: {m['action']}")

# 检查 action
actions = models.execute('app', uid, 'admin', 'ir.actions.act_window', 'search_read',
    [('id', '=', 143)],
    ['id', 'name', 'res_model', 'context', 'domain'])
    
print("\n=== Contacts Action (ID 143) ===")
for a in actions:
    print(f"Context: {a.get('context')}")
    print(f"Domain: {a.get('domain')}")
