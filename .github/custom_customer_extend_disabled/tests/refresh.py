#!/usr/bin/env python3
"""
清除缓存
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 清除缓存
models.execute('app', uid, 'admin', 'ir.config_parameter', 'search_read',
    [('key', '=', 'web.base.url')], [])

print("已刷新")

# Amanda 测试
amanda_uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})
partners = models.execute('app', amanda_uid, 'Odoo123456', 'res.partner', 'search_read', 
    [], ['name'], 0, 10)
print(f"Amanda 可见联系人: {len(partners)}")
for p in partners[:5]:
    print(f"  - {p['name']}")
