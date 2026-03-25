#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 采购组ID=72
user_names = ['Spring', 'Crystal', 'Susan', 'Sunny']
for name in user_names:
    ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', name)]])
    if ids:
        models.execute_kw(db, uid, password, 'res.users', 'write', [ids[0], {
            'group_ids': [(4, 72)]
        }])
        print(f"Added {name} to 采购组")

print("Done!")