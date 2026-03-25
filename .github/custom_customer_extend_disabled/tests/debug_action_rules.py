#!/usr/bin/env python3
import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取 action model ID
action_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
    [('model', '=', 'ir.actions.act_window')], ['id'])
action_model_id = action_model[0]['id']

# 检查规则
rules = models.execute('app', uid, 'admin', 'ir.rule', 'search_read',
    [('model_id', '=', action_model_id)],
    ['name', 'domain_force', 'global', 'groups'])

print('=== ir.actions.act_window 规则 ===')
for r in rules:
    print(f'\n规则: {r["name"]}')
    print(f'  global: {r["global"]}')
    print(f'  domain: {r.get("domain_force", "N/A")[:100]}...' if r.get("domain_force") else '  domain: N/A')
    print(f'  groups: {r.get("groups")}')
