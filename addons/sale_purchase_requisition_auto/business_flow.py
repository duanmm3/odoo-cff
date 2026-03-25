#!/usr/bin/env python3
import xmlrpc.client
import time

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*60)
print("完整业务流程验证")
print("="*60)

# 步骤1: Alan创建销售订单
print("\n步骤1: Alan创建销售订单(产品cff3, 数量110)")
partner = [935]
product = [10]
alan = 21

sale_id = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'create', [{
    'partner_id': partner[0],
    'order_line': [[0, 0, {'product_id': product[0], 'product_uom_qty': 110, 'price_unit': 10}]]
}])
print(f"  销售订单: {sale_id}")

# 确认订单
models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'action_confirm', [sale_id])
print("  订单已确认")

time.sleep(1)

# 步骤2: 检查是否有采购需求生成
print("\n步骤2: 检查采购需求(Purchase Requisition)")
pr_all = models.execute_kw(db, uid, 'admin', 'purchase.requisition', 'search', [[('id', '>=', 0)]])
print(f"  采购需求总数: {len(pr_all)}")

# 检查新创建的采购需求
pr_alan = models.execute_kw(db, alan, 'Odoo123456', 'purchase.requisition', 'search', [[('id', '>=', 0)]])
print(f"  Alan可见采购需求: {len(pr_alan)}")

# 步骤3: Susan查看采购需求
print("\n步骤3: Susan查看采购需求")
susan = 39
pr_susan = models.execute_kw(db, susan, 'Odoo123456', 'purchase.requisition', 'search', [[('id', '>=', 0)]])
print(f"  Susan可见采购需求: {len(pr_susan)}")

# 步骤4: 库存检查
print("\n步骤4: 检查产品库存")
stock = models.execute_kw(db, uid, 'admin', 'product.product', 'read', [10, ['name', 'qty_available', 'virtual_available']])
print(f"  cff3库存: {stock}")

# 步骤5: Alan创建发票
print("\n步骤5: Alan创建发票")
# 获取已确认的销售订单
confirmed_so = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'search', [['state', '=', 'sale']])
print(f"  Alan的销售订单: {confirmed_so}")

if confirmed_so:
    # 创建发票
    invoice_id = models.execute_kw(db, alan, 'Odoo123456', 'sale.order', 'action_invoice', [confirmed_so[0]])
    print(f"  发票创建: {invoice_id}")

# 步骤6: 库存验证
print("\n步骤6: 最终库存检查")
stock = models.execute_kw(db, uid, 'admin', 'product.product', 'read', [10, ['name', 'qty_available']])
print(f"  cff3最终库存: {stock}")

print("\n" + "="*60)
print("业务流程验证完成!")
print("="*60)