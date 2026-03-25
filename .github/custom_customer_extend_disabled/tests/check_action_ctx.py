#!/usr/bin/env python3
"""
检查 action context
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查 action 143
action = models.execute('app', uid, 'admin', 'ir.actions.act_window', 'search_read',
    [('id', '=', 143)],
    ['name', 'context', 'domain'])

print("=== Action 143 ===")
for a in action:
    print(f"Context: {a['context']}")
    print(f"Domain: {a['domain']}")
