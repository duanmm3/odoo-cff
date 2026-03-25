#!/usr/bin/env python3
"""
完整的 web 界面模拟测试
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# Amanda 登录
amanda = common.authenticate('app', 'Amanda', 'Odoo123456', {})

print("=== Amanda Web 界面测试 ===")

# 1. 测试 session/info
try:
    result = models.execute('app', amanda, 'Odoo123456', 'res.users', 'search_read',
        [('id', '=', amanda)],
        ['id', 'name', 'login', 'company_ids'])
    print(f"1. 用户信息: ✓")
    for r in result:
        print(f"   {r['name']} - {r['login']}")
except Exception as e:
    print(f"1. 用户信息: ✗ {e}")

# 2. 测试公司访问
try:
    result = models.execute('app', amanda, 'Odoo123456', 'res.company', 'search_read',
        [],
        ['name'], 0, 5)
    print(f"2. 公司列表: ✓ ({len(result)} 条)")
except Exception as e:
    print(f"2. 公司列表: ✗ {e}")

# 3. 测试配置参数
try:
    result = models.execute('app', amanda, 'Odoo123456', 'ir.config_parameter', 'search_read',
        [('key', '=', 'web.base.url')],
        ['value'])
    print(f"3. 配置参数: ✓")
except Exception as e:
    print(f"3. 配置参数: ✗ {e}")

# 4. 测试菜单
try:
    result = models.execute('app', amanda, 'Odoo123456', 'ir.ui.menu', 'search_read',
        [('parent_id', '=', False)],
        ['name'], 0, 10)
    print(f"4. 根菜单: ✓ ({len(result)} 条)")
except Exception as e:
    print(f"4. 根菜单: ✗ {e}")

# 5. 测试完整联系人搜索
try:
    result = models.execute('app', amanda, 'Odoo123456', 'res.partner', 'search_read',
        [],
        ['name', 'email', 'phone'], 0, 10)
    print(f"5. 联系人列表: ✓ ({len(result)} 条)")
    for r in result[:3]:
        print(f"   - {r['name']}")
except Exception as e:
    print(f"5. 联系人列表: ✗ {e}")

print("\n=== 完成 ===")
