#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 检查这些组ID
group_ids = [22, 27, 67, 21, 9, 52, 16, 1, 24, 30, 44, 35, 8, 53, 4, 51]
groups = models.execute_kw(db, uid, password, 'res.groups', 'read', [group_ids, ['name']])
for g in groups:
    print(f"Group {g['id']}: {g['name']}")