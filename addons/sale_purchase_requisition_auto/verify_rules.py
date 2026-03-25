#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("验证权限")
print("="*60)

# Admin查看 - 应该看到全部
admin_po = models.execute_kw(db, uid, 'admin', 'purchase.order', 'search', [[('id', '>=', 0)]])
print(f"Admin采购订单: {len(admin_po)}")

admin_so = models.execute_kw(db, uid, 'admin', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Admin销售订单: {len(admin_so)}")

time.sleep(1)

# Alan(销售组)查看
alan_uid = common.authenticate(db, 'Alan', 'Odoo123456', {})
print(f"\nAlan(销售)登录: {alan_uid}")

# 检查Alan的user_id在采购订单中的记录
if alan_uid:
    alan_po = models.execute_kw(db, alan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
    print(f"Alan-采购订单: {len(alan_po)}")
    
    alan_so = models.execute_kw(db, alan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
    print(f"Alan-销售订单: {len(alan_so)}")

time.sleep(1)

# Susan(采购组)查看
susan_uid = common.authenticate(db, 'Susan', 'Odoo123456', {})
print(f"\nSusan(采购)登录: {susan_uid}")

if susan_uid:
    susan_po = models.execute_kw(db, susan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
    print(f"Susan-采购订单: {len(susan_po)}")
    
    susan_so = models.execute_kw(db, susan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
    print(f"Susan-销售订单: {len(susan_so)}")

print("\n" + "="*60)
print("结果:")
print("="*60)
print(f"管理员: 采购={len(admin_po)}, 销售={len(admin_so)}")
print(f"销售(Alan): 采购={len(alan_po)}, 销售={len(alan_so)}")
print(f"采购(Susan): 采购={len(susan_po)}, 销售={len(susan_so)}")

if len(alan_po) < len(admin_po):
    print("\n✓ 销售组只能看到部分采购订单!")
else:
    print("\n✗ 销售组可以看到全部采购订单 - 规则未生效")

if len(susan_so) < len(admin_so):
    print("✓ 采购组只能看到部分销售订单!")
else:
    print("✗ 采购组可以看到全部销售订单 - 规则未生效")