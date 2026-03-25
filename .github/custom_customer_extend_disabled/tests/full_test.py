#!/usr/bin/env python3
"""
完整模拟页面加载
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

print("=== 1. 测试联系人搜索 ===")
partners = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', 
    [], ['name', 'email', 'phone'], 0, 10)
print(f"找到 {len(partners)} 个联系人")
for p in partners[:5]:
    print(f"  - {p['name']}")

print("\n=== 2. 测试列表视图 ===")
# 获取列表视图
views = models.execute('app', uid, 'Odoo123456', 'ir.ui.view', 'search',
    [('model', '=', 'res.partner'), ('type', '=', 'list'), ('active', '=', True)])
print(f"列表视图数量: {len(views)}")

print("\n=== 3. 测试搜索视图 ===")
search_views = models.execute('app', uid, 'Odoo123456', 'ir.ui.view', 'search',
    [('model', '=', 'res.partner'), ('type', '=', 'search'), ('active', '=', True)])
print(f"搜索视图数量: {len(search_views)}")

print("\n=== 4. 测试 action ===")
action = models.execute('app', uid, 'Odoo123456', 'ir.actions.act_window', 'read',
    [143], ['name', 'view_mode', 'context'])
print(f"Action: {action}")

print("\n=== 5. 完整测试 ===")
# 模拟完整搜索
ctx = {'default_is_company': True}
result = models.execute_kw('app', uid, 'Odoo123456', 'res.partner', 'search_read',
    [[], ['name']], {'limit': 5})
print(f"结果: {result}")
