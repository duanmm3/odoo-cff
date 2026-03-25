#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("步骤1: Alan创建销售订单(产品cff3, 数量110)")
print("="*60)
partner, product = [935], [10]
alan = 21

sale_id = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'create', [{
    'partner_id': partner[0],
    'order_line': [[0, 0, {'product_id': product[0], 'product_uom_qty': 110, 'price_unit': 10}]]
}])
print(f"销售订单: {sale_id}")

models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'action_confirm', [sale_id])
print("订单已确认")

time.sleep(1)

print("\n" + "="*60)
print("步骤2: 验证权限")
print("="*60)

# Alan查看
alan_po = models.execute_kw(db, alan, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
alan_so = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Alan(销售组): 采购订单={len(alan_po)}, 销售订单={len(alan_so)}")

# Susan查看
susan = common.authenticate(db, 'Susan', 'Odoo123456', {})
susan_po = models.execute_kw(db, susan, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
susan_so = models.execute_kw(db, susan, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Susan(采购组): 采购订单={len(susan_po)}, 销售订单={len(susan_so)}")

# Admin查看
admin_po = models.execute_kw(db, uid, 'admin', 'purchase.order', 'search', [[('id', '>=', 0)]])
admin_so = models.execute_kw(db, uid, 'admin', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Admin(管理员): 采购订单={len(admin_po)}, 销售订单={len(admin_so)}")

print("\n" + "="*60)
print("步骤3: 检查采购需求(Purchase Requisition)")
print("="*60)

# 检查是否有采购需求
pr_admin = models.execute_kw(db, uid, 'admin', 'purchase.requisition', 'search', [[('id', '>=', 0)]])
print(f"Admin看到的采购需求: {len(pr_admin)}")

pr_alan = models.execute_kw(db, alan, 'Odoo123456', 'purchase.requisition', 'search', [[('id', '>=', 0)]])
print(f"Alan看到的采购需求: {len(pr_alan)}")

print("\n" + "="*60)
print("验证完成!")
print("="*60)