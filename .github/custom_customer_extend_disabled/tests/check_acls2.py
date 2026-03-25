#!/usr/bin/env python3
"""
检查 res.partner 的 ACL
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取 partner 模型ID
partner_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read', 
    [('model', '=', 'res.partner')], ['id'])
partner_model_id = partner_model[0]['id']

# 获取 ACL
acls = models.execute('app', uid, 'admin', 'ir.model.access', 'search_read',
    [('model_id', '=', partner_model_id)],
    ['name', 'group_id', 'perm_read'])

print("=== res.partner ACL ===")
for a in acls:
    print(f"{a['name']}: {a['group_id']} - read={a['perm_read']}")
