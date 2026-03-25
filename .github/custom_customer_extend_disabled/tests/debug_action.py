#!/usr/bin/env python3
import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

# 用 Amanda 登录
uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})

# 测试直接用 action 读取数据
action_id = 143  # Contacts action
result = models.execute('app', uid, 'Odoo123456', 'ir.actions.act_window', 'read',
    [action_id], ['name', 'res_model', 'view_mode'])
print('Action:', result)

# 尝试用 action 的上下文搜索
ctx = {'active_model': 'res.partner'}
partners = models.execute('app', uid, 'Odoo123456', 'res.partner', 'search_read', 
    [], ['name', 'email'], 0, 10)
print(f'\n搜索到 {len(partners)} 个联系人')
