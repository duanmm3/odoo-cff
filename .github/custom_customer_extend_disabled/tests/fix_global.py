#!/usr/bin/env python3
"""
修复全局规则
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取 partner 模型ID
partner_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read', 
    [('model', '=', 'res.partner')], ['id'])
partner_model_id = partner_model[0]['id']

# 修改全局规则
global_rule = models.execute('app', uid, 'admin', 'ir.rule', 'search',
    [('model_id', '=', partner_model_id), ('global', '=', True)])

models.execute('app', uid, 'admin', 'ir.rule', 'write', global_rule, {
    'domain_force': "[(1, '=', 1)]"
})

print("✓ 已修改全局规则为允许所有")
