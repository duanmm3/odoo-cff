#!/usr/bin/env python3
"""
检查 Amanda 的联系人数据
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# 用 admin 检查 Amanda 的联系人
uid = common.authenticate('app', 'admin', 'admin', {})

# Amanda 的 UID
amanda_uid = 138

# Amanda 创建的联系人
created = models.execute('app', uid, 'admin', 'res.partner', 'search_read',
    [('create_uid', '=', amanda_uid)], ['name'])
print(f"Amanda 创建的联系人: {len(created)}")
for p in created[:5]:
    print(f"  - {p['name']}")

# 共享给 Amanda 的联系人
shared = models.execute('app', uid, 'admin', 'res.partner', 'search_read',
    [('shared_users', 'in', [amanda_uid])], ['name'])
print(f"\n共享给 Amanda 的联系人: {len(shared)}")
for p in shared[:5]:
    print(f"  - {p['name']}")

# 总计
total = models.execute('app', uid, 'admin', 'res.partner', 'search_count',
    ['|', ('create_uid', '=', amanda_uid), ('shared_users', 'in', [amanda_uid])])
print(f"\n总计: {total}")
