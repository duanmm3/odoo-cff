#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("1. 升级模块...")
module_ids = models.execute_kw(db, uid, 'admin', 'ir.module.module', 'search', [[('name', '=', 'sale_purchase_requisition_auto')]])
if module_ids:
    models.execute_kw(db, uid, 'admin', 'ir.module.module', 'button_immediate_upgrade', [module_ids])
    print("   模块已升级")

print("2. 检查产品cff3...")
product_ids = models.execute_kw(db, uid, 'admin', 'product.product', 'search', [[('name', '=', 'cff3')]])
print(f"   产品ID: {product_ids}")

print("3. 检查用户Alan...")
alan_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', 'Alan')]])
print(f"   Alan ID: {alan_ids}")

print("4. 检查用户Susan...")
susan_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', 'Susan')]])
print(f"   Susan ID: {susan_ids}")

print("5. 检查仓库...")
warehouse_ids = models.execute_kw(db, uid, 'admin', 'stock.warehouse', 'search', [])
print(f"   仓库ID: {warehouse_ids}")

print("完成!")