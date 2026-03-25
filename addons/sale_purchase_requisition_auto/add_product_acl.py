#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("添加产品访问权限...")

# 获取模型ID
product_model = models.execute_kw(db, uid, 'admin', 'ir.model', 'search', [[('model', '=', 'product.product')]])
print(f"产品模型: {product_model}")

product_template_model = models.execute_kw(db, uid, 'admin', 'ir.model', 'search', [[('model', '=', 'product.template')]])
print(f"产品模板模型: {product_template_model}")

# 获取组ID
sales_group = 76
purchase_group = 75

# 销售组的产品权限
sales_acl = [
    {
        'name': 'product.product.sales team',
        'model_id': product_model[0] if product_model else 53,
        'group_id': sales_group,
        'perm_read': True,
        'perm_create': True,
        'perm_write': True,
        'perm_unlink': True,
    },
    {
        'name': 'product.template.sales team',
        'model_id': product_template_model[0] if product_template_model else 54,
        'group_id': sales_group,
        'perm_read': True,
        'perm_create': True,
        'perm_write': True,
        'perm_unlink': True,
    }
]

# 采购组的产品权限
purchase_acl = [
    {
        'name': 'product.product.purchase team',
        'model_id': product_model[0] if product_model else 53,
        'group_id': purchase_group,
        'perm_read': True,
        'perm_create': True,
        'perm_write': True,
        'perm_unlink': True,
    },
    {
        'name': 'product.template.purchase team',
        'model_id': product_template_model[0] if product_template_model else 54,
        'group_id': purchase_group,
        'perm_read': True,
        'perm_create': True,
        'perm_write': True,
        'perm_unlink': True,
    }
]

# 创建销售组权限
for acl in sales_acl:
    acl_id = models.execute_kw(db, uid, 'admin', 'ir.model.access', 'create', [acl])
    print(f"创建销售组ACL: {acl_id}")

# 创建采购组权限
for acl in purchase_acl:
    acl_id = models.execute_kw(db, uid, 'admin', 'ir.model.access', 'create', [acl])
    print(f"创建采购组ACL: {acl_id}")

print("\n完成!")