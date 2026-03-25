#!/usr/bin/env python3
"""模拟业务流程：销售订单及库存管理"""

import xmlrpc.client
import sys

HOST = 'localhost'
PORT = 8070  # 使用8070端口
DB = 'app'
USER = 'admin'
PASS = 'admin'

sock = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
common = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/common')

uid = common.authenticate(DB, USER, PASS, {})
print(f"登录成功，uid={uid}")

def search(model, domain, fields=None):
    if fields:
        return sock.execute(DB, uid, PASS, model, 'search_read', domain, fields)
    else:
        ids = sock.execute(DB, uid, PASS, model, 'search', domain)
        return ids

def create(model, vals):
    return sock.execute(DB, uid, PASS, model, 'create', vals)

def write(model, ids, vals):
    return sock.execute(DB, uid, PASS, model, 'write', ids, vals)

def unlink(model, ids):
    return sock.execute(DB, uid, PASS, model, 'unlink', ids)

def execute(model, method, *args):
    return sock.execute(DB, uid, PASS, model, method, *args)

def get_latest_quants(warehouse_id, product_id, limit=5):
    """获取指定仓库和产品的最新库存记录"""
    loc_ids = search('stock.location', [('warehouse_id', '=', warehouse_id), ('usage', '=', 'internal')])
    if not loc_ids:
        return []
    domain = [
        ('product_id', '=', product_id),
        ('location_id', 'in', loc_ids),
    ]
    # 使用正确的参数格式
    return sock.execute(DB, uid, PASS, 'stock.quant', 'search_read', 
        domain, ['id', 'quantity', 'in_date', 'location_id'])

print("\n========== 步骤1：创建产品 ==========")

# 检查是否已存在产品
pa001_ids = search('product.product', [('default_code', '=', 'pa001')])
pb001_ids = search('product.product', [('default_code', '=', 'pb001')])

print(f"pa001 已有: {pa001_ids}")
print(f"pb001 已有: {pb001_ids}")

# 创建产品pa001
if not pa001_ids:
    # 创建产品模板（Odoo会自动创建对应的product.product）
    template_id = create('product.template', {
        'name': 'PA001产品',
        'type': 'consu',  # Goods type
        'is_storable': True,  # Enable inventory tracking
        'tracking': 'lot',
        'default_code': 'pa001',
        'list_price': 10,
        'standard_price': 5,
    })
    # 获取自动创建的产品变体
    pa001_id = search('product.product', [('product_tmpl_id', '=', template_id)])[0]
    print(f"创建产品pa001，id={pa001_id}")
else:
    pa001_id = pa001_ids[0]
    # 更新为storable product
    product_data = search('product.product', [('id', '=', pa001_id)], ['product_tmpl_id'])
    if product_data:
        template_id = product_data[0]['product_tmpl_id'][0]
        write('product.template', [template_id], {'is_storable': True, 'tracking': 'lot'})
    print(f"使用已有产品pa001，id={pa001_id}")

# 创建产品pb001
if not pb001_ids:
    template_id = create('product.template', {
        'name': 'PB001产品',
        'type': 'consu',
        'is_storable': True,
        'tracking': 'lot',
        'default_code': 'pb001',
        'list_price': 20,
        'standard_price': 10,
    })
    pb001_id = search('product.product', [('product_tmpl_id', '=', template_id)])[0]
    print(f"创建产品pb001，id={pb001_id}")
else:
    pb001_id = pb001_ids[0]
    # 更新为storable product
    product_data = search('product.product', [('id', '=', pb001_id)], ['product_tmpl_id'])
    if product_data:
        template_id = product_data[0]['product_tmpl_id'][0]
        write('product.template', [template_id], {'is_storable': True, 'tracking': 'lot'})
    print(f"使用已有产品pb001，id={pb001_id}")

print("\n========== 步骤2：创建仓库 ==========")

# 检查仓库
cff_com_ids = search('stock.warehouse', [('name', 'ilike', 'CFF-com')])
cff_hk_ids = search('stock.warehouse', [('name', 'ilike', 'CFF-HK')])

print(f"CFF-com 已有: {cff_com_ids}")
print(f"CFF-HK 已有: {cff_hk_ids}")

if not cff_com_ids:
    cff_com_id = create('stock.warehouse', {
        'name': 'CFF-com',
        'code': 'CFF1',
    })
    print(f"创建仓库CFF-com，id={cff_com_id}")
else:
    cff_com_id = cff_com_ids[0]
    print(f"使用已有仓库CFF-com，id={cff_com_id}")

if not cff_hk_ids:
    cff_hk_id = create('stock.warehouse', {
        'name': 'CFF-HK',
        'code': 'CFF2',
    })
    print(f"创建仓库CFF-HK，id={cff_hk_id}")
else:
    cff_hk_id = cff_hk_ids[0]
    print(f"使用已有仓库CFF-HK，id={cff_hk_id}")

print("\n========== 步骤3：创建批次号 ==========")

# 创建批次号 202601
lot_ids = search('stock.lot', [('name', '=', '202601'), ('product_id', '=', pa001_id)])
if not lot_ids:
    lot_pa001_id = create('stock.lot', {
        'name': '202601',
        'product_id': pa001_id,
        'company_id': 1,
    })
    print(f"创建批次号202601 for pa001，id={lot_pa001_id}")
else:
    lot_pa001_id = lot_ids[0]
    print(f"使用已有批次号202601 for pa001，id={lot_pa001_id}")

lot_ids2 = search('stock.lot', [('name', '=', '202601'), ('product_id', '=', pb001_id)])
if not lot_ids2:
    lot_pb001_id = create('stock.lot', {
        'name': '202601',
        'product_id': pb001_id,
        'company_id': 1,
    })
    print(f"创建批次号202601 for pb001，id={lot_pb001_id}")
else:
    lot_pb001_id = lot_ids2[0]
    print(f"使用已有批次号202601 for pb001，id={lot_pb001_id}")

print("\n========== 步骤4：设置初始库存 ==========")

# 获取仓库位置
locations = search('stock.location', [('warehouse_id', '=', cff_com_id), ('usage', '=', 'internal')])
loc_com_id = locations[0] if locations else None
print(f"CFF-com 库存位置: {loc_com_id}")

locations_hk = search('stock.location', [('warehouse_id', '=', cff_hk_id), '|', ('usage', '=', 'internal'), ('usage', '=', 'view')], ['id', 'usage'])
loc_hk_id = None
for loc in locations_hk:
    if isinstance(loc, dict) and loc.get('usage') == 'internal':
        loc_hk_id = loc['id']
        break
    elif not isinstance(loc, dict) and loc == 14:  # fallback to known location
        loc_hk_id = loc
        break
if loc_hk_id is None:
    loc_hk_id = 14  # Use known HK warehouse location
print(f"CFF-HK 库存位置: {loc_hk_id}")

# 检查库存是否已存在
def get_stock_qty(product_id, location_id):
    domain = [
        ('product_id', '=', product_id),
        ('location_id', '=', location_id),
    ]
    quants = search('stock.quant', domain, ['quantity'])
    return sum(q['quantity'] for q in quants) if quants else 0

# 显示各仓库的库存情况
print("\n--- 当前库存情况 ---")
for wh_id, wh_name in [(cff_com_id, 'CFF-com'), (cff_hk_id, 'CFF-HK')]:
    print(f"\n{wh_name}:")
    for prod_id, prod_name, prod_code in [(pa001_id, 'pa001', 'PA001'), (pb001_id, 'pb001', 'PB001')]:
        latest = get_latest_quants(wh_id, prod_id)[:3]  # 只显示前3条
        qty = get_stock_qty(prod_id, loc_com_id if wh_name == 'CFF-com' else loc_hk_id)
        print(f"  {prod_name}: 总库存={qty}")
        if latest:
            for q in latest:
                print(f"    - id={q['id']}, qty={q['quantity']}, date={q['in_date']}")

# 检查并设置CFF-com库存
com_pa001_qty = get_stock_qty(pa001_id, loc_com_id)
com_pb001_qty = get_stock_qty(pb001_id, loc_com_id)
if com_pa001_qty == 0 and com_pb001_qty == 0:
    # 只有库存为0时才添加初始库存
    create('stock.quant', {'product_id': pa001_id, 'location_id': loc_com_id, 'quantity': 100, 'lot_id': lot_pa001_id})
    create('stock.quant', {'product_id': pb001_id, 'location_id': loc_com_id, 'quantity': 100, 'lot_id': lot_pb001_id})
    print(f"\nCFF-com 初始库存已添加: pa001=100, pb001=100")
else:
    print(f"\nCFF-com 已有库存: pa001={com_pa001_qty}, pb001={com_pb001_qty}，跳过添加")

# 检查并设置CFF-HK库存
hk_pa001_qty = get_stock_qty(pa001_id, loc_hk_id)
hk_pb001_qty = get_stock_qty(pb001_id, loc_hk_id)
if hk_pa001_qty == 0 and hk_pb001_qty == 0:
    create('stock.quant', {'product_id': pa001_id, 'location_id': loc_hk_id, 'quantity': 100, 'lot_id': lot_pa001_id})
    create('stock.quant', {'product_id': pb001_id, 'location_id': loc_hk_id, 'quantity': 100, 'lot_id': lot_pb001_id})
    print(f"CFF-HK 初始库存已添加: pa001=100, pb001=100")
else:
    print(f"CFF-HK 已有库存: pa001={hk_pa001_qty}, pb001={hk_pb001_qty}，跳过添加")

print("\n========== 步骤5：检查初始库存 ==========")

# 查询各仓库库存
def get_stock(product_id, warehouse_id):
    domain = [
        ('product_id', '=', product_id),
        ('warehouse_id', '=', warehouse_id),
    ]
    quants = search('stock.quant', domain, ['quantity', 'location_id'])
    return quants

# 检查CFF-com库存
quants_com_pa001 = get_stock(pa001_id, cff_com_id)
quants_com_pb001 = get_stock(pb001_id, cff_com_id)
print(f"CFF-com pa001库存: {quants_com_pa001}")
print(f"CFF-com pb001库存: {quants_com_pb001}")

# 检查CFF-HK库存
quants_hk_pa001 = get_stock(pa001_id, cff_hk_id)
quants_hk_pb001 = get_stock(pb001_id, cff_hk_id)
print(f"CFF-HK pa001库存: {quants_hk_pa001}")
print(f"CFF-HK pb001库存: {quants_hk_pb001}")

# 使用库存盘点查询
print("\n--- 使用库存盘点查询 ---")
for wh_id, wh_name in [(cff_com_id, 'CFF-com'), (cff_hk_id, 'CFF-HK')]:
    for prod_id, prod_name in [(pa001_id, 'pa001'), (pb001_id, 'pb001')]:
        domain = [
            ('product_id', '=', prod_id),
            ('location_id.warehouse_id', '=', wh_id),
            ('location_id.usage', '=', 'internal'),
        ]
        quants = search('stock.quant', domain, ['quantity', 'lot_id'])
        total = sum(q.get('quantity', 0) for q in quants)
        print(f"{wh_name} - {prod_name}: {total}")

print("\n========== 步骤6：创建销售订单 ==========")

# 查找或创建客户Suwen
partner_ids = search('res.partner', [('name', 'ilike', 'Suwen')])
if partner_ids:
    partner_id = partner_ids[0]
    print(f"使用已有客户Suwen，id={partner_id}")
else:
    partner_id = create('res.partner', {
        'name': 'Suwen',
        'company_type': 'company',
    })
    print(f"创建客户Suwen，id={partner_id}")

# 查找销售负责人
user_ids = search('res.users', [('login', '=', 'Suwen')])
if user_ids:
    user_id = user_ids[0]
else:
    user_id = uid  # 使用admin
print(f"销售负责人: {user_id}")

# 创建销售订单
sale_order_id = create('sale.order', {
    'partner_id': partner_id,
    'user_id': user_id,
    'warehouse_id': cff_hk_id,  # 指定CFF-HK仓库
    'picking_policy': 'direct',
})

# 添加销售订单行
create('sale.order.line', {
    'order_id': sale_order_id,
    'product_id': pa001_id,
    'name': 'PA001产品',
    'product_uom_qty': 30,
    'price_unit': 10,
})

create('sale.order.line', {
    'order_id': sale_order_id,
    'product_id': pb001_id,
    'name': 'PB001产品',
    'product_uom_qty': 20,
    'price_unit': 20,
})

print(f"创建销售订单，id={sale_order_id}")

# 确认销售订单
execute('sale.order', 'action_confirm', [sale_order_id])
print("销售订单已确认")

# 检查生成的出库单
picking_ids = search('stock.picking', [('sale_id', '=', sale_order_id)])
print(f"生成的出库单: {picking_ids}")

# 验证出库
if picking_ids:
    for pick_id in picking_ids:
        execute('stock.picking', 'button_validate', [pick_id])
        print(f"出库单 {pick_id} 已完成")

print("\n========== 步骤7：开票收款 ==========")

# 创建发票
so_name = search('sale.order', [('id', '=', sale_order_id)], ['name'])
so_name = so_name[0]['name'] if so_name else f'SO{sale_order_id}'
invoice_ids = search('account.move', [('invoice_origin', '=', so_name)])
print(f"已有发票: {invoice_ids}")

if not invoice_ids:
    # 创建发票并直接确认
    invoice_id = create('account.move', {
        'move_type': 'out_invoice',
        'partner_id': partner_id,
        'invoice_origin': so_name,
        'invoice_line_ids': [
            (0, 0, {
                'product_id': pa001_id,
                'quantity': 30,
                'price_unit': 10,
            }),
            (0, 0, {
                'product_id': pb001_id,
                'quantity': 20,
                'price_unit': 20,
            }),
        ],
    })
    invoice_ids = [invoice_id]
    print(f"创建发票: {invoice_id}")

if invoice_ids:
    # 确认发票
    execute('account.move', 'action_post', invoice_ids)
    print(f"发票 {invoice_ids} 已确认")
    print("注: 收款流程需要更多配置，跳过")

print("\n========== 步骤8：最终库存核对 ==========")

print("\n--- 最终库存查询 ---")
for wh_id, wh_name in [(cff_com_id, 'CFF-com'), (cff_hk_id, 'CFF-HK')]:
    for prod_id, prod_name in [(pa001_id, 'pa001'), (pb001_id, 'pb001')]:
        domain = [
            ('product_id', '=', prod_id),
            ('location_id.warehouse_id', '=', wh_id),
            ('location_id.usage', '=', 'internal'),
        ]
        quants = search('stock.quant', domain, ['quantity', 'lot_id'])
        total = sum(q.get('quantity', 0) for q in quants)
        print(f"{wh_name} - {prod_name}: {total}")

print("\n========== 流程完成 ==========")
print("期望结果：")
print("  - CFF-HK pa001: 70 (原来100，销售30)")
print("  - CFF-HK pb001: 80 (原来100，销售20)")
print("  - CFF-com pa001: 100 (未动)")
print("  - CFF-com pb001: 100 (未动)")