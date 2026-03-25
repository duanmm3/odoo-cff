#!/usr/bin/env python3
"""
直接修改 action
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 修改 action 143 的 context
models.execute('app', uid, 'admin', 'ir.actions.act_window', 'write', [143], {
    'context': "{'default_is_company': True, 'search_default_my_contacts': 1}"
})

print("✓ 已修改 action 143")

# 验证
action = models.execute('app', uid, 'admin', 'ir.actions.act_window', 'search_read',
    [('id', '=', 143)],
    ['context'])
print(f"New context: {action[0]['context']}")
