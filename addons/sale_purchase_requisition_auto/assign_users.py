#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 组ID: 采购组=72, 销售组=73, 管理员组=74
purchase_group_id = 72
sales_group_id = 73
admin_group_id = 74

# 采购组用户: Buyer, Spring, Crystal, Susan, Sunny
purchase_users = ['Buyer', 'Spring', 'Crystal', 'Susan', 'Sunny']
for user_name in purchase_users:
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
    if user_ids:
        # 先获取当前用户的组
        user = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids[0], ['group_ids']])
        current_groups = user[0]['group_ids'] if user else []
        # 添加采购组
        current_groups.append(purchase_group_id)
        models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids[0], {
            'group_ids': [[6, 0, current_groups]]
        }])
        print(f"Added {user_name} to 采购组")

# 管理员组用户: Coco, cc
admin_users = ['Coco', 'cc']
for user_name in admin_users:
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
    if user_ids:
        user = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids[0], ['group_ids']])
        current_groups = user[0]['group_ids'] if user else []
        current_groups.append(admin_group_id)
        models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids[0], {
            'group_ids': [[6, 0, current_groups]]
        }])
        print(f"Added {user_name} to 管理员组")

# 销售组用户 (不包括 sale2, Huabin, Lillia - 需要确认是否存在)
sales_users = ['Alan', 'Amanda', 'Cathy', 'Emma', 'Ferpa', 'Milne', 'sale1', 'sales', 'Suwen', 'Vivian']
for user_name in sales_users:
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[('name', '=', user_name)]])
    if user_ids:
        user = models.execute_kw(db, uid, password, 'res.users', 'read', [user_ids[0], ['group_ids']])
        current_groups = user[0]['group_ids'] if user else []
        current_groups.append(sales_group_id)
        models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids[0], {
            'group_ids': [[6, 0, current_groups]]
        }])
        print(f"Added {user_name} to 销售组")

print("User assignment done!")