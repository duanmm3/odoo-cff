#!/usr/bin/env python3
import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 查找 contacts 菜单和 action
# 先找到 action
actions = models.execute('app', uid, 'admin', 'ir.actions.act_window', 'search_read',
    [('res_model', '=', 'res.partner')],
    ['id', 'name', 'xml_id'])
print('=== Contact Actions ===')
for a in actions[:10]:
    xml_id = a.get('xml_id', '')
    print(f'  {a["name"]} (ID: {a["id"]}) - {xml_id}')

# 查找 menu
menus = models.execute('app', uid, 'admin', 'ir.ui.menu', 'search_read',
    [('name', 'ilike', 'contact')],
    ['id', 'name', 'action'])
print('\n=== Contact Menus ===')
for m in menus[:10]:
    print(f'  {m["name"]} (ID: {m["id"]}) - Action: {m["action"]}')
