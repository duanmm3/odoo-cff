#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("创建销售订单...")
partner, product = [935], [10]
alan = 21

sale_id = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'create', [{
    'partner_id': partner[0],
    'order_line': [[0, 0, {'product_id': product[0], 'product_uom_qty': 110, 'price_unit': 10}]]
}])
print(f"订单: {sale_id}")

time.sleep(1)

models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'action_confirm', [sale_id])
print("已确认")

time.sleep(1)

print("Alan查看...")
alan_po = models.execute_kw(db, alan, 'Odoo123456', 'purchase.order', 'search', [[('id', '>=', 0)]])
print(f"Alan采购: {len(alan_po)}")

alan_so = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'search', [[('id', '>=', 0)]])
print(f"Alan销售: {len(alan_so)}")

print("完成")