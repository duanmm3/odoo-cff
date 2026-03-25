#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("步骤1: 添加用户到对应组")
print("="*60)

# 销售组ID=76, 采购组ID=75, 管理员组ID=77
sales_group = 76
purchase_group = 75
admin_group = 77

# 销售组用户
sales_users = ['Alan', 'Amanda', 'Cathy', 'Emma', 'Ferpa', 'Milne', 'Suwen', 'Vivian']
for name in sales_users:
    user_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [user_ids[0], ['group_ids']])
        groups = user[0]['group_ids']
        if sales_group not in groups:
            groups.append(sales_group)
            models.execute_kw(db, uid, 'admin', 'res.users', 'write', [user_ids[0], {'group_ids': [[6, 0, groups]]}])
            print(f"  {name} -> 销售组")

# 采购组用户
purchase_users = ['Spring', 'Crystal', 'Susan', 'Sunny']
for name in purchase_users:
    user_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [user_ids[0], ['group_ids']])
        groups = user[0]['group_ids']
        if purchase_group not in groups:
            groups.append(purchase_group)
            models.execute_kw(db, uid, 'admin', 'res.users', 'write', [user_ids[0], {'group_ids': [[6, 0, groups]]}])
            print(f"  {name} -> 采购组")

time.sleep(1)

print("\n" + "="*60)
print("步骤2: 验证用户组分配")
print("="*60)

alan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [21, ['group_ids']])
print(f"Alan组: {alan[0]['group_ids']}")

susan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [39, ['group_ids']])
print(f"Susan组: {susan[0]['group_ids']}")

time.sleep(1)

print("\n" + "="*60)
print("步骤3: 测试权限")
print("="*60)

# Alan登录
alan_uid = common.authenticate(db, 'Alan', 'Odoo123456', {})
print(f"Alan登录: {alan_uid}")

# Alan查看采购和销售订单
alan_po = models.execute_kw(db, alan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
print(f"Alan-采购订单: {len(alan_po)}")

alan_so = models.execute_kw(db, alan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Alan-销售订单: {len(alan_so)}")

# Susan登录
susan_uid = common.authenticate(db, 'Susan', 'Odoo123456', {})
print(f"Susan登录: {susan_uid}")

susan_po = models.execute_kw(db, susan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
print(f"Susan-采购订单: {len(susan_po)}")

susan_so = models.execute_kw(db, susan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Susan-销售订单: {len(susan_so)}")

# Admin查看
admin_po = models.execute_kw(db, uid, 'admin', 'purchase.order', 'search', [[('id', '>=', 0)]])
print(f"Admin-采购订单: {len(admin_po)}")

admin_so = models.execute_kw(db, uid, 'admin', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Admin-销售订单: {len(admin_so)}")

print("\n" + "="*60)
print("权限测试结果:")
print("="*60)
print(f"销售(Alan): 采购={len(alan_po)}, 销售={len(alan_so)}")
print(f"采购(Susan): 采购={len(susan_po)}, 销售={len(susan_so)}")
print(f"管理员: 采购={len(admin_po)}, 销售={len(admin_so)}")

print("\n完成!")