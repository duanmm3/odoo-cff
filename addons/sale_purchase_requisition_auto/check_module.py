#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("检查模块状态...")
module = models.execute_kw(db, uid, 'admin', 'ir.module.module', 'search', 
    [[('name', '=', 'sale_purchase_requisition_auto')]])
print(f"模块: {module}")

if module:
    state = models.execute_kw(db, uid, 'admin', 'ir.module.module', 'read', [module[0], ['state', 'name']])
    print(f"状态: {state}")

print("\n检查自定义记录规则...")
# 搜索包含我们组ID的规则
rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'search_read', 
    [[('groups', 'in', [75, 76])], ['name', 'groups', 'model_id']])
print(f"规则: {rules}")

print("\n检查Alan的user_id...")
alan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [21, ['id', 'name', 'login']])
print(f"Alan: {alan}")