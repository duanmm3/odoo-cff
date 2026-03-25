#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("检查Susan的组...")
susan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [39, ['group_ids']])
print(f"Susan组: {susan[0]['group_ids']}")

print("\n添加Susan到采购组...")
susan_groups = susan[0]['group_ids']
if 75 not in susan_groups:
    susan_groups.append(75)
    models.execute_kw(db, uid, 'admin', 'res.users', 'write', [39, {'group_ids': [[6, 0, susan_groups]]}])
    print("已添加Susan到采购组")
else:
    print("Susan已在采购组")

# 验证
susan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [39, ['group_ids']])
print(f"Susan新组: {susan[0]['group_ids']}")