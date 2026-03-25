#!/usr/bin/env python3
import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

# 测试读取联系人
partners = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', [], ['name'])
print(f'联系人数量: {len(partners)}')
print(f'前3个: {[p["name"] for p in partners[:3]]}')

# 测试搜索视图
views = models.execute('app', uid, 'Odoo123456', 'ir.ui.view', 'search_read',
    [('model', '=', 'res.partner'), ('type', '=', 'list')],
    ['name', 'id'])
print(f'\n联系人列表视图数量: {len(views)}')
for v in views[:5]:
    print(f'  - {v["name"]} (ID: {v["id"]})')
