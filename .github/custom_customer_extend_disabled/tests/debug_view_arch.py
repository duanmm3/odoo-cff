#!/usr/bin/env python3
import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 查找自定义的 list view
views = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
    [('model', '=', 'res.partner'), ('type', '=', 'list'), ('name', 'like', 'custom')],
    ['id', 'name', 'active', 'inherit_id'])
print('=== Custom List Views ===')
for v in views:
    print(f'  {v["name"]} (ID: {v["id"]}) - Active: {v["active"]}')

# 检查视图是否有问题 - 尝试读取 arch
if views:
    view_id = views[0]['id']
    view = models.execute('app', uid, 'admin', 'ir.ui.view', 'search_read',
        [('id', '=', view_id)],
        ['arch_db', 'active'])
    print(f'\nView arch (first 500 chars):')
    print(view[0]['arch_db'][:500] if view[0].get('arch_db') else 'No arch')
