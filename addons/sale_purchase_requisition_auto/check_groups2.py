#!/usr/bin/env python3
import xmlrpc.client
import sys

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 搜索包含 Sales 或 Purchase 的组
sales_groups = models.execute_kw(db, uid, password, 'res.groups', 'search_read', 
    [[('name', 'ilike', 'Sales')]], {'fields': ['name', 'id']})
print("Sales groups:", sales_groups[:5])

purchase_groups = models.execute_kw(db, uid, password, 'res.groups', 'search_read', 
    [[('name', 'ilike', 'Purchase')]], {'fields': ['name', 'id']})
print("Purchase groups:", purchase_groups[:5])