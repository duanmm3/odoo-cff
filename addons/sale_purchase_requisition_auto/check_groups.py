#!/usr/bin/env python3
import xmlrpc.client
import sys

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f"Logged in as uid: {uid}")

if not uid:
    print("Failed to authenticate")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

sales_group = models.execute_kw(db, uid, password, 'res.groups', 'search', [[('name', '=', 'Sales / Salesman')]])
purchase_group = models.execute_kw(db, uid, password, 'res.groups', 'search', [[('name', '=', 'Purchase / User')]])

print(f"Sales group: {sales_group}")
print(f"Purchase group: {purchase_group}")

# Get all groups for user Milne
user_ids = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[('name', '=', 'Milne')], ['group_ids']], {'limit': 1})
print(f"User Milne groups: {user_ids}")

print("Done!")