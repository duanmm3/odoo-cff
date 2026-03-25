#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("检查并修复组权限")
print("="*60)

# 销售组(76)需要销售权限
# 采购组(75)需要采购权限

# 检查销售组是否有销售订单的访问权限
print("\n1. 检查销售权限...")
sale_access = models.execute_kw(db, uid, 'admin', 'ir.model.access', 'search', [
    [('name', 'ilike', 'sale.order'), ('group_id', '=', 76)]
])
print(f"销售组(76)销售订单访问权限: {sale_access}")

if not sale_access:
    # 获取sales_team.group_sale_salesman的ID
    sales_team_group = models.execute_kw(db, uid, 'admin', 'res.groups', 'search', 
        [[('name', '=', 'Sales / Salesman')]])
    print(f"Sales / Salesman组: {sales_team_group}")

print("\n2. 检查采购权限...")
# 检查采购组是否有采购订单的访问权限
purchase_access = models.execute_kw(db, uid, 'admin', 'ir.model.access', 'search', 
    [['name', 'ilike', 'purchase.order'], ['group_id', '=', 75]])
print(f"采购组(75)采购订单访问权限: {purchase_access}")

# 获取purchase.group_purchase_user的ID
purchase_group = models.execute_kw(db, uid, 'admin', 'res.groups', 'search', 
    [[('name', '=', 'Purchase / User')]])
print(f"Purchase / User组: {purchase_group}")

print("\n3. 检查当前用户的完整权限...")
# 检查Alan的完整组
alan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [21, ['group_ids']])
print(f"Alan组: {alan[0]['group_ids']}")

# 检查Susan的完整组
susan = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [39, ['group_ids']])
print(f"Susan组: {susan[0]['group_ids']}")

print("\n完成检查")