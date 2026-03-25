#!/usr/bin/env python3
"""
检查 res.users 访问
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
amanda = common.authenticate('app', 'Amanda', 'Odoo123456', {})

print("=== Amanda 访问 res.users ===")

try:
    # 测试读取自己的用户信息
    user = models.execute('app', amanda, 'Odoo123456', 'res.users', 'read', [amanda], ['name', 'login'])
    print(f"用户信息: {user}")
except Exception as e:
    print(f"错误: {e}")

# 检查 ACL
admin = common.authenticate('app', 'admin', 'admin', {})
user_model = models.execute('app', admin, 'admin', 'ir.model', 'search_read',
    [('model', '=', 'res.users')], ['id'])
user_model_id = user_model[0]['id']

acls = models.execute('app', admin, 'admin', 'ir.model.access', 'search_read',
    [('model_id', '=', user_model_id)],
    ['name', 'group_id', 'perm_read'])

print("\n=== res.users ACL ===")
for a in acls:
    print(f"{a['name']}: {a['group_id']} - read={a['perm_read']}")
