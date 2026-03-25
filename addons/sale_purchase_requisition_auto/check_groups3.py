#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

all_groups = models.execute_kw(db, uid, password, 'res.groups', 'search_read', 
    [[('category_id.name', 'ilike', 'Sales')]], {'fields': ['name', 'id', 'category_id']})
print("Sales category groups:", all_groups)

all_groups = models.execute_kw(db, uid, password, 'res.groups', 'search_read', 
    [[('category_id.name', 'ilike', 'Purchase')]], {'fields': ['name', 'id', 'category_id']})
print("Purchase category groups:", all_groups)