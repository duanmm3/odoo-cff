#!/usr/bin/env python3
"""
检查需要哪些模型的权限
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 检查哪些模型需要权限
models_to_check = [
    'ir.ui.menu',
    'ir.model.data',
    'ir.model',
    'ir.default',
    'res.config.settings',
]

for model_name in models_to_check:
    try:
        model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
            [('model', '=', model_name)], ['id'])
        if model:
            # 检查 ACL
            acls = models.execute('app', uid, 'admin', 'ir.model.access', 'search_read',
                [('model_id', '=', model[0]['id'])],
                ['name', 'group_id'])
            print(f'\n=== {model_name} (ID: {model[0]["id"]}) ===')
            for a in acls[:5]:
                print(f'  {a["name"]}: group {a["group_id"]}')
    except Exception as e:
        print(f'{model_name}: Error - {e}')
