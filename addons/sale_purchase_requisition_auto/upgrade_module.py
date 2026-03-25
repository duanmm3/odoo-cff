#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("升级模块...")
# 升级模块
module_ids = models.execute_kw(db, uid, 'admin', 'ir.module.module', 'search', 
    [[('name', '=', 'sale_purchase_requisition_auto')]])
if module_ids:
    try:
        models.execute_kw(db, uid, 'admin', 'ir.module.module', 'button_immediate_upgrade', [module_ids])
        print("模块已升级")
    except Exception as e:
        print(f"升级时出错: {e}")

print("\n检查产品访问权限...")
# 检查销售组的产品访问权限
sales_group = models.execute_kw(db, uid, 'admin', 'res.groups', 'search', [[('name', '=', 'Sales Team (销售组)')]])
print(f"销售组: {sales_group}")

# 检查采购组的产品访问权限
purchase_group = models.execute_kw(db, uid, 'admin', 'res.groups', 'search', [[('name', '=', 'Purchase Team (采购组)')]])
print(f"采购组: {purchase_group}")

print("\n完成!")