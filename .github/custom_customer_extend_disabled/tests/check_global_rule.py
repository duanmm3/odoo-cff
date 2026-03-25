#!/usr/bin/env python3
"""
检查全局规则 - 看看是否影响了其他模型
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查 res.partner 的全局规则
partner_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
    [('model', '=', 'res.partner')], ['id'])
partner_model_id = partner_model[0]['id']

rules = models.execute('app', uid, 'admin', 'ir.rule', 'search_read',
    [('model_id', '=', partner_model_id), ('global', '=', True)],
    ['name', 'domain_force'])

print('=== res.partner 全局规则 ===')
for r in rules:
    print(f'\n规则: {r["name"]}')
    print(f'  domain: {r.get("domain_force")}')
