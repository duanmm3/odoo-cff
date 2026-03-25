#!/usr/bin/env python3
"""
清理所有自定义权限规则
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

# 删除所有自定义规则
rules_to_delete = [
    'res.partner: user filter',
    'res.partner: admin rule', 
    'res.partner: all access',
    'res.partner: admin all',
]

for rule_name in rules_to_delete:
    rules = models.execute('app', uid, 'admin', 'ir.rule', 'search',
        [('model_id', '=', partner_model_id), ('name', '=', rule_name)])
    if rules:
        models.execute('app', uid, 'admin', 'ir.rule', 'unlink', rules)
        print(f'已删除规则: {rule_name}')

# 恢复全局规则
global_rule = models.execute('app', uid, 'admin', 'ir.rule', 'search',
    [('model_id', '=', partner_model_id), ('global', '=', True)])

if global_rule:
    models.execute('app', uid, 'admin', 'ir.rule', 'write', global_rule, {
        'domain_force': "['|', '|', ('partner_share', '=', False), ('company_id', 'parent_of', user.company_id.id), ('company_id', '=', False)]"
    })
    print('已恢复全局规则')

print('\n清理完成!')
