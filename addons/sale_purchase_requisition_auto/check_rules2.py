#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("检查采购订单记录规则...")
rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'read', [[169, 171, 221, 222], ['name', 'groups', 'domain_force', 'model_id']])
for r in rules:
    print(f"  {r['name']}: groups={r['groups']}")

print("\n检查销售订单记录规则...")
rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'read', [[127, 130, 132, 133], ['name', 'groups', 'domain_force', 'model_id']])
for r in rules:
    print(f"  {r['name']}: groups={r['groups']}")