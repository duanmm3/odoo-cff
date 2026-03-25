#!/usr/bin/env python3
"""
检查规则
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

# 获取规则
rules = models.execute('app', uid, 'admin', 'ir.rule', 'search_read',
    [('model_id', '=', partner_model_id)],
    ['name', 'domain_force', 'global', 'groups'])

print("=== res.partner 规则 ===")
for r in rules:
    print(f"\n{r['name']}: global={r['global']}")
    print(f"  domain: {r.get('domain_force', 'N/A')}")
