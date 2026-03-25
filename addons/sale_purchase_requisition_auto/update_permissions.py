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

# 查找新创建的组
purchase_group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[('name', '=', '采购组')]])
sales_group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[('name', '=', '销售组')]])
admin_group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[('name', '=', '管理员组')]])

print(f"Purchase group: {purchase_group_ids}")
print(f"Sales group: {sales_group_ids}")
print(f"Admin group: {admin_group_ids}")

# 采购组用户: Buyer, Spring, Crystal, Susan, Sunny
purchase_users = ['Buyer', 'Spring', 'Crystal', 'Susan', 'Sunny']
# 管理员组用户: Coco, cc (admin已经默认有管理员权限)
admin_users = ['Coco', 'cc']
# 销售组用户: Alan, Amanda, Cathy, Emma, Ferpa, Huabin, Lillia, Milne, sale1, sale2, sales, Suwen, test, Vivian
sales_users = ['Alan', 'Amanda', 'Cathy', 'Emma', 'Ferpa', 'Huabin', 'Lillia', 'Milne', 'sale1', 'sale2', 'sales', 'Suwen', 'test', 'Vivian']

if purchase_group_ids:
    for user_name in purchase_users:
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
        if user_ids:
            # 添加到采购组
            models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids[0], {
                'group_ids': [(4, purchase_group_ids[0])]
            }])
            print(f"Added {user_name} to 采购组")

if admin_group_ids:
    for user_name in admin_users:
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
        if user_ids:
            # 添加到管理员组
            models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids[0], {
                'group_ids': [(4, admin_group_ids[0])]
            }])
            print(f"Added {user_name} to 管理员组")

if sales_group_ids:
    for user_name in sales_users:
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
        if user_ids:
            # 添加到销售组
            models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids[0], {
                'group_ids': [(4, sales_group_ids[0])]
            }])
            print(f"Added {user_name} to 销售组")

print("Done!")