#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("=== 创建销售订单 ===")
partner = [935]
product = [10]

# Alan创建销售订单
alan = 21
sale_id = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'create', [{
    'partner_id': partner[0],
    'order_line': [[0, 0, {'product_id': product[0], 'product_uom_qty': 110, 'price_unit': 10}]]
}])
print(f"销售订单: {sale_id}")

models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'action_confirm', [sale_id])
print("已确认")

print("\n=== 验证权限 ===")
# Alan查看
alan_po = models.execute_kw(db, alan, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
alan_so = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Alan-采购:{len(alan_po)}, 销售:{len(alan_so)}")

# Susan查看
susan = common.authenticate(db, 'Susan', 'Odoo123456', {})
susan_po = models.execute_kw(db, susan, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
susan_so = models.execute_kw(db, susan, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Susan-采购:{len(susan_po)}, 销售:{len(susan_so)}")

# Admin查看
admin_po = models.execute_kw(db, uid, 'admin', 'purchase.order', 'search', [[('id', '>=', 0)]])
admin_so = models.execute_kw(db, uid, 'admin', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Admin-采购:{len(admin_po)}, 销售:{len(admin_so)}")

print("\n完成!")