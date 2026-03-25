#!/usr/bin/env python3
"""
检查用户菜单访问
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
amanda = common.authenticate('app', 'Amanda', 'Odoo123456', {})
admin = common.authenticate('app', 'admin', 'admin', {})

print("=== Amanda 的菜单访问 ===")

# 获取菜单
menus = models.execute('app', amanda, 'Odoo123456', 'ir.ui.menu', 'search_read',
    [('name', 'ilike', 'Contact')],
    ['id', 'name'])

print(f"找到 {len(menus)} 个联系人相关菜单")
for m in menus:
    print(f"  - {m['name']} (ID: {m['id']})")

print("\n=== Amanda 的可用操作 ===")
# 获取 act_window
actions = models.execute('app', amanda, 'Odoo123456', 'ir.actions.act_window', 'search_read',
    [('res_model', '=', 'res.partner')],
    ['id', 'name'])

print(f"找到 {len(actions)} 个联系人相关操作")
for a in actions[:5]:
    print(f"  - {a['name']} (ID: {a['id']})")

print("\n=== 测试直接访问 ===")
# 尝试用 action 读取
try:
    result = models.execute('app', amanda, 'Odoo123456', 'ir.actions.act_window', 'read', [143], ['name'])
    print(f"Action 143: {result}")
except Exception as e:
    print(f"Action 143 错误: {e}")
