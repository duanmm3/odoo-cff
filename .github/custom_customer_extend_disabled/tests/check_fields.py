#!/usr/bin/env python3
"""
检查 shared_users 字段是否存在
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查字段
fields = models.execute('app', uid, 'admin', 'ir.model.fields', 'search_read',
    [('model', '=', 'res.partner'), ('name', 'in', ['shared_users', 'partner_code'])],
    ['name', 'ttype'])

print("=== res.partner 字段 ===")
for f in fields:
    print(f"{f['name']}: {f['ttype']}")
