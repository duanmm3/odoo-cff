#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("验证用户和组")
print("="*60)

for name in ['Alan', 'Susan']:
    user_ids = models.execute_kw(db, uid, 'admin', 'res.users', 'search', [[('name', '=', name)]])
    if user_ids:
        user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [user_ids[0], ['name', 'group_ids']])
        print(f"  {name}: ID={user_ids[0]}, Groups={user[0]['group_ids']}")

print("\n检查产品cff3...")
product_ids = models.execute_kw(db, uid, 'admin', 'product.product', 'search', [[('name', '=', 'cff3')]])
if product_ids:
    product = models.execute_kw(db, uid, 'admin', 'product.product', 'read', [product_ids[0], ['name', 'qty_available']])
    print(f"  产品: {product[0]}")

# 获取第一个客户
partner_ids = models.execute_kw(db, uid, 'admin', 'res.partner', 'search', [[('id', '>', 0)]], {'limit': 1})
print(f"  客户ID: {partner_ids}")

print("\n" + "="*60)
print("Alan创建销售订单")
print("="*60)

# Alan登录
alan_uid = common.authenticate(db, 'Alan', 'Odoo123456', {})
print(f"  Alan登录成功, uid={alan_uid}")

if alan_uid and product_ids and partner_ids:
    # 创建销售订单
    sale_order_id = models.execute_kw(db, alan_uid, 'Odoo123456', 'sale.order', 'create', [{
        'partner_id': partner_ids[0],
        'order_line': [[0, 0, {
            'product_id': product_ids[0],
            'product_uom_qty': 110,
            'price_unit': 10.0
        }]]
    }])
    print(f"  销售订单创建成功: ID={sale_order_id}")
    
    # 确认订单
    models.execute_kw(db, alan_uid, 'Odoo123456', 'sale.order', 'action_confirm', [sale_order_id])
    print(f"  订单已确认")

print("\n" + "="*60)
print("验证权限")
print("="*60)

# Alan查看采购订单
alan_po = models.execute_kw(db, alan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>', 0)]])
print(f"  Alan看到采购订单数: {len(alan_po)}")

# Alan查看销售订单
alan_so = models.execute_kw(db, alan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>', 0)]])
print(f"  Alan看到销售订单数: {len(alan_so)}")

print("\n" + "="*60)
print("Susan查看")
print("="*60)

susan_uid = common.authenticate(db, 'Susan', 'Odoo123456', {})
print(f"  Susan登录成功, uid={susan_uid}")

if susan_uid:
    susan_po = models.execute_kw(db, susan_uid, 'Odoo123456', 'purchase.order', 'search', [[('id', '>', 0)]])
    print(f"  Susan看到采购订单数: {len(susan_po)}")
    susan_so = models.execute_kw(db, susan_uid, 'Odoo123456', 'sale.order', 'search', [[('id', '>', 0)]])
    print(f"  Susan看到销售订单数: {len(susan_so)}")

print("\n完成!")