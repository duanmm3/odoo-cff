#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 检查Alan和Susan的组
print("检查用户组...")
alan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [21, ['group_ids']])
print(f"Alan: {alan[0]['group_ids']}")

susan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [39, ['group_ids']])
print(f"Susan: {susan[0]['group_ids']}")

# Alan登录测试
print("\nAlan登录...")
alan_uid = common.authenticate(db, 'Alan', 'Odoo123456', {})
print(f"Alan uid: {alan_uid}")

if alan_uid:
    alan_po = models.execute_kw(db, alan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
    print(f"Alan采购订单: {len(alan_po)}")
    
    alan_so = models.execute_kw(db, alan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
    print(f"Alan销售订单: {len(alan_so)}")

print("完成")