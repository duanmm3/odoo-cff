#!/usr/bin/env python3
import xmlrpc.client
import sys

url = 'http://localhost:8070'
db = 'app'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("步骤1: 升级模块")
print("="*60)
module_ids = models.execute_kw(db, uid, 'admin', 'ir.module.module', 'search', [[('name', '=', 'sale_purchase_requisition_auto')]])
if module_ids:
    models.execute_kw(db, uid, 'admin', 'ir.module.module', 'button_immediate_upgrade', [module_ids])
    print("模块已升级")
else:
    print("模块未找到")

print("\n" + "="*60)
print("步骤2: 创建/验证用户组")
print("="*60)

# 检查现有组
existing_groups = models.execute_kw(db, uid, 'admin', 'res.groups', 'search', [[('name', 'in', ['Purchase Team (采购组)', 'Sales Team (销售组)', 'Admin Team (管理员组)'])]])
print(f"现有组: {existing_groups}")

if not existing_groups:
    # 创建组
    purchase_group_id = models.execute_kw(db, uid, 'admin', 'res.groups', 'create', [{'name': 'Purchase Team (采购组)'}])
    sales_group_id = models.execute_kw(db, uid, 'admin', 'res.groups', 'create', [{'name': 'Sales Team (销售组)'}])
    admin_group_id = models.execute_kw(db, uid, 'admin', 'res.groups', 'create', [{'name': 'Admin Team (管理员组)'}])
    print(f"创建组: 采购={purchase_group_id}, 销售={sales_group_id}, 管理员={admin_group_id}")
else:
    purchase_group_id = 72
    sales_group_id = 73
    admin_group_id = 74
    print(f"使用现有组: 采购={purchase_group_id}, 销售={sales_group_id}, 管理员={admin_group_id}")

print("\n" + "="*60)
print("步骤3: 分配用户到组")
print("="*60)

# 销售组用户
sales_users = ['Alan', 'Amanda', 'Cathy', 'Emma', 'Ferpa', 'Milne', 'sale1', 'sales', 'Suwen', 'Vivian']
# 采购组用户
purchase_users = ['Spring', 'Crystal', 'Susan', 'Sunny']
# 管理员组用户
admin_users = ['Coco', 'cc']

for name in sales_users:
    user_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [user_ids[0], ['group_ids']])
        groups = user[0]['group_ids']
        if sales_group_id not in groups:
            groups.append(sales_group_id)
            models.execute_kw(db, uid, 'admin', 'res.users', 'write', [user_ids[0], {'group_ids': [[6, 0, groups]]}])
            print(f"  {name} -> 销售组")

for name in purchase_users:
    user_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [user_ids[0], ['group_ids']])
        groups = user[0]['group_ids']
        if purchase_group_id not in groups:
            groups.append(purchase_group_id)
            models.execute_kw(db, uid, 'admin', 'res.users', 'write', [user_ids[0], {'group_ids': [[6, 0, groups]]}])
            print(f"  {name} -> 采购组")

for name in admin_users:
    user_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [user_ids[0], ['group_ids']])
        groups = user[0]['group_ids']
        if admin_group_id not in groups:
            groups.append(admin_group_id)
            models.execute_kw(db, uid, 'admin', 'res.users', 'write', [user_ids[0], {'group_ids': [[6, 0, groups]]}])
            print(f"  {name} -> 管理员组")

print("\n用户分配完成!")
print("="*60)