import odoorpc
from datetime import datetime, timedelta

odoo = odoorpc.ODOO('localhost', port=8070, protocol='jsonrpc')

print("="*60)
print("完整业务流程测试")
print("="*60)

# 获取产品ID
product_id = 9
warehouse_id = 2

# 步骤1: Milne 创建销售订单
print("\n[1] Milne 创建销售订单 (2100个)")
odoo.login('app', 'Milne', 'Odoo123456')
env = odoo.env
product_model = env['product.product']
partner_model = env['res.partner']

milne = partner_model.search_read([('name', '=', 'Milne')], ['id'])
partner_id = milne[0]['id'] if milne else 1

so_model = env['sale.order']
so_id = so_model.create({
    'partner_id': partner_id,
    'partner_invoice_id': partner_id,
    'partner_shipping_id': partner_id,
    'warehouse_id': warehouse_id,
})
so = so_model.browse(so_id)
so.write({'order_line': [(0, 0, {
    'product_id': product_id,
    'product_uom_qty': 2100.0,
    'price_unit': 15.0,
})]})
print(f"  销售订单: {so.name}")

# 步骤2: Milne 创建采购申请
print("\n[2] Milne 创建采购申请")
pr_model = env['purchase.requisition']
planned_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

pr_id = pr_model.create({
    'name': 'PR-TEST-001',
    'vendor_id': 1,
    'requisition_type': 'blanket_order',
    'date_start': '2026-03-24',
    'warehouse_id': warehouse_id,
})
pr = pr_model.browse(pr_id)
pr.write({'line_ids': [(0, 0, {
    'product_id': product_id,
    'product_qty': 2100.0,
    'product_uom_id': 1,
    'price_unit': 15.0,
})]})
pr.write({'state': 'confirmed'})
print(f"  采购申请: {pr.name}")

# 步骤3: Susan 创建采购订单
print("\n[3] Susan 创建采购订单")
odoo.login('app', 'Susan', 'Odoo123456')
env = odoo.env
product_model = env['product.product']

po_model = env['purchase.order']
po_id = po_model.create({
    'partner_id': 1,
    'date_planned': planned_date,
    'order_line': [(0, 0, {
        'product_id': product_id,
        'product_qty': 2100.0,
        'product_uom_id': 1,
        'price_unit': 15.0,
        'date_planned': planned_date,
    })]
})
po = po_model.browse(po_id)
print(f"  采购订单: {po.name}")

# 步骤4: Susan 确认订单
print("\n[4] Susan 确认采购订单")
po.button_confirm()
po = po_model.browse(po_id)
print(f"  状态: {po.state}")

# 步骤5: Admin 审批
print("\n[5] Admin 经理审批")
odoo.login('app', 'admin', 'admin')
env = odoo.env
product_model = env['product.product']

po = po_model.browse(po_id)
po.button_approve()
po.button_confirm()
po = po_model.browse(po_id)
print(f"  状态: {po.state}")

# 步骤6: 入库
print("\n[6] 入库")
sp_model = env['stock.picking']
sps = sp_model.search_read([('origin', '=', po.name)], ['id', 'name', 'state'])
print(f"  入库单: {len(sps)}")

if sps:
    sp = sp_model.browse(sps[0]['id'])
    move = sp.move_ids[0]
    
    # 设置数量
    lot_model = env['stock.lot']
    lots = lot_model.search_read([('name', '=', '2137'), ('product_id', '=', product_id)], ['id'])
    lot_id = lots[0]['id'] if lots else None
    
    move_line_model = env['stock.move.line']
    move_line_model.create({
        'move_id': move.id,
        'product_id': product_id,
        'lot_id': lot_id,
        'quantity': 2100.0,
        'product_uom_id': 1,
        'location_id': move.location_id.id,
        'location_dest_id': move.location_dest_id.id,
        'picking_id': sp.id,
    })
    move.write({'picked': True})
    sp.button_validate()
    print(f"  入库完成")

# 步骤7: 库存
print("\n[7] 最终库存")
product = product_model.browse(product_id)
print(f"  产品: {product.name}")
print(f"  可用库存: {product.qty_available}")
print(f"  虚拟库存: {product.virtual_available}")

print("\n" + "="*60)
print("业务流程测试完成!")
print("="*60)
