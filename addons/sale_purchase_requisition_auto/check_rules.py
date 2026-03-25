#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("检查现有记录规则...")
# 检查purchase.order的记录规则
po_rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'search', [[('model_id.model', '=', 'purchase.order')]])
print(f"Purchase Order记录规则: {po_rules}")

# 检查sale.order的记录规则  
so_rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'search', [[('model_id.model', '=', 'sale.order')]])
print(f"Sale Order记录规则: {so_rules}")

# 检查组
groups = models.execute_kw(db, uid, 'admin', 'res.groups', 'search', [[('name', 'ilike', 'Team')]])
print(f"组: {groups}")

if groups:
    group_details = models.execute_kw(db, uid, 'admin', 'res.groups', 'read', [groups, ['name']])
    print(f"组详情: {group_details}")