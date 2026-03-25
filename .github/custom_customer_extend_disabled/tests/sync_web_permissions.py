#!/usr/bin/env python3
"""
同步权限到 web 界面需要的模型
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# web 界面需要的模型
models_needed = [
    'bus.presence',
    'bus.channel',
    'ir.websocket',
    'ir.config_parameter',
    'res.company',
    'res.currency',
    'mail.message',
    'mail.channel',
]

# 获取 group_user ID
group_user_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1

print("=== 添加 Web 界面需要的权限 ===")

for model_name in models_needed:
    # 获取模型ID
    model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
        [('model', '=', model_name)], ['id'])
    if not model:
        print(f'  - {model_name}: 未找到')
        continue
    
    model_id = model[0]['id']
    
    # 检查是否已有 ACL
    existing = models.execute('app', uid, 'admin', 'ir.model.access', 'search',
        [('model_id', '=', model_id), ('group_id', '=', group_user_id)])
    
    if not existing:
        try:
            acl_id = models.execute('app', uid, 'admin', 'ir.model.access', 'create', {
                'name': f'{model_name}_user_access',
                'model_id': model_id,
                'group_id': group_user_id,
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
            })
            print(f'✓ {model_name}: ACL 已创建')
        except Exception as e:
            print(f'✗ {model_name}: {str(e)[:30]}')
    else:
        print(f'- {model_name}: 已存在')

print("\n=== 完成 ===")
