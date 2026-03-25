#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

# 测试Milne创建产品
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
milne_uid = common.authenticate(db, 'Milne', 'Odoo123456', {})
print(f"Milne登录: {milne_uid}")

if milne_uid:
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # 尝试创建产品
    try:
        product_id = models.execute_kw(db, milne_uid, 'Odoo123456', 'product.product', 'create', [{
            'name': '测试产品-Milne',
            'type': 'consu',
            'list_price': 100,
        }])
        print(f"产品创建成功: {product_id}")
    except Exception as e:
        print(f"创建失败: {e}")

print("\n完成!")