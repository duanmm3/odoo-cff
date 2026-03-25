#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 搜索特定用户
names = ['Buyer', 'Spring', 'Crystal', 'Susan', 'Sunny', 'Coco', 'admin', 'cc', 
         'Alan', 'Amanda', 'Cathy', 'Emma', 'Ferpa', 'Huabin', 'Lillia', 'Milne', 
         'sale1', 'sales', 'Suwen', 'test', 'Vivian']

for name in names:
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids[0], ['name', 'group_ids']])
        print(f"{name}: id={user_ids[0]}, groups={user[0]['group_ids']}")