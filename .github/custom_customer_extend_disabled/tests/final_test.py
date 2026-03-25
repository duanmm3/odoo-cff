#!/usr/bin/env python3
"""
最终验证测试
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

print("=== 测试各用户 ===")

# Amanda
amanda = common.authenticate('app', 'Amanda', 'Odoo123456', {})
p = models.execute('app', amanda, 'Odoo123456', 'res.partner', 'search_count', [])
print(f"Amanda: {p} 条联系人")

# Susan
susann = common.authenticate('app', 'Susan', 'Odoo123456', {})
p = models.execute('app', susann, 'Odoo123456', 'res.partner', 'search_count', [])
print(f"Susan: {p} 条联系人")

# admin
admin = common.authenticate('app', 'admin', 'admin', {})
p = models.execute('app', admin, 'admin', 'res.partner', 'search_count', [])
print(f"admin: {p} 条联系人")

print("\n=== 权限测试 ===")

# Amanda 创建联系人测试
new_id = models.execute('app', amanda, 'Odoo123456', 'res.partner', 'create', {
    'name': '测试联系人_Amanda'
})
print(f"✓ Amanda 创建成功: {new_id}")

# Amanda 修改
models.execute('app', amanda, 'Odoo123456', 'res.partner', 'write', new_id, {
    'name': '测试联系人_Amanda_修改'
})
print(f"✓ Amanda 修改成功")

print("\n=== 完成 ===")
