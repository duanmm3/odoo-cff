#!/usr/bin/env python3
"""
测试当前状态
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

print("=== 测试 ===")

# Amanda 登录
amanda = common.authenticate('app', 'Amanda', 'Odoo123456', {})
print(f"Amanda UID: {amanda}")

# 搜索联系人
partners = models.execute('app', amanda, 'Odoo123456', 'res.partner', 'search_read', 
    [], ['name'], 0, 10)
print(f"联系人数量: {len(partners)}")
for p in partners[:5]:
    print(f"  - {p['name']}")
