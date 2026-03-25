#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 创建采购组
purchase_group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [{
    'name': '采购组'
}])
print(f"Created Purchase group: {purchase_group_id}")

# 创建销售组
sales_group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [{
    'name': '销售组'
}])
print(f"Created Sales group: {sales_group_id}")

# 创建管理员组
admin_group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [{
    'name': '管理员组'
}])
print(f"Created Admin group: {admin_group_id}")

print("Groups created!")