#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
print(f"Admin: {uid}")

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 客户
partner = models.execute_kw(db, uid, 'admin', 'res.partner', 'search', [[('id', '>', 0)]], {'limit': 1})
print(f"Partner: {partner}")

# 产品
product = models.execute_kw(db, uid, 'admin', 'product.product', 'search', [[('name', '=', 'cff3')]])
print(f"Product: {product}")

# Alan
alan = common.authenticate(db, 'Alan', 'Odoo123456', {})
print(f"Alan: {alan}")