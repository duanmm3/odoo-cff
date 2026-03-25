#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("手动创建记录规则")
print("="*60)

# 获取purchase.order的model_id
po_model = models.execute_kw(db, uid, 'admin', 'ir.model', 'search', [[('model', '=', 'purchase.order')]])
print(f"Purchase Order model: {po_model}")

# 获取sale.order的model_id
so_model = models.execute_kw(db, uid, 'admin', 'ir.model', 'search', [[('model', '=', 'sale.order')]])
print(f"Sale Order model: {so_model}")

# 销售组(76)只能看自己的采购订单
print("\n创建销售组采购订单规则...")
rule1 = models.execute_kw(db, uid, 'admin', 'ir.rule', 'create', [{
    'name': '销售组只能看自己的采购订单',
    'model_id': po_model[0],
    'groups': [[6, 0, [76]]],
    'domain_force': "[('user_id', '=', user.id)]"
}])
print(f"规则1: {rule1}")

# 采购组(75)只能看自己的销售订单
print("\n创建采购组销售订单规则...")
rule2 = models.execute_kw(db, uid, 'admin', 'ir.rule', 'create', [{
    'name': '采购组只能看自己的销售订单',
    'model_id': so_model[0],
    'groups': [[6, 0, [75]]],
    'domain_force': "[('user_id', '=', user.id)]"
}])
print(f"规则2: {rule2}")

print("\n完成!")