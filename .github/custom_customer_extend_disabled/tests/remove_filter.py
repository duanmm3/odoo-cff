#!/usr/bin/env python3
"""
修改 action - 移除默认过滤器
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 修改 action 143 移除过滤器
models.execute('app', uid, 'admin', 'ir.actions.act_window', 'write', [143], {
    'context': "{'default_is_company': True}"
})

print("✓ 已移除默认过滤器")

# 验证
action = models.execute('app', uid, 'admin', 'ir.actions.act_window', 'search_read',
    [('id', '=', 143)],
    ['context'])
print(f"New context: {action[0]['context']}")
