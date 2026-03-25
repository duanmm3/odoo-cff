#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 使用 id >= 1 作为域
all_group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[('id', '>=', 1)]])
print(f"Total groups: {len(all_group_ids)}")

# 读取所有组的名称
groups = models.execute_kw(db, uid, password, 'res.groups', 'read', [all_group_ids[:80], ['name']])
for g in groups:
    print(f"  {g['id']}: {g['name']}")