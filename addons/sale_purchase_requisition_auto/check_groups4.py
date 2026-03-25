#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 列出所有组
all_groups = models.execute_kw(db, uid, password, 'res.groups', 'search_read', 
    [[('name', 'ilike', 'Sale')]], {'fields': ['name', 'id']})
print("Groups with 'Sale':", all_groups)

all_groups = models.execute_kw(db, uid, password, 'res.groups', 'search_read', 
    [[('name', 'ilike', 'Purchase')]], {'fields': ['name', 'id']})
print("Groups with 'Purchase':", all_groups)