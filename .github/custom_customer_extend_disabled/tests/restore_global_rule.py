#!/usr/bin/env python3
"""
恢复全局规则到原始状态
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取 partner 模型ID
partner_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
    [('model', '=', 'res.partner')], ['id'])
partner_model_id = partner_model[0]['id']

# 恢复原始全局规则
global_rule = models.execute('app', uid, 'admin', 'ir.rule', 'search',
    [('model_id', '=', partner_model_id), ('global', '=', True), ('name', '=', 'res.partner company')])

if global_rule:
    models.execute('app', uid, 'admin', 'ir.rule', 'write', global_rule, {
        'domain_force': "['|', '|', ('partner_share', '=', False), ('company_id', 'parent_of', user.company_id.id), ('company_id', '=', False)]"
    })
    print(f'✓ 已恢复全局规则: {global_rule}')
else:
    print('未找到全局规则')
