#!/usr/bin/env python3
"""
添加必要的 ACL
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 需要添加权限的模型
models_to_add = [
    'ir.ui.view',
    'ir.model.data',
]

# 获取 group_user ID
group_user_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1

for model_name in models_to_add:
    # 获取模型ID
    model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
        [('model', '=', model_name)], ['id'])
    if not model:
        print(f'未找到模型: {model_name}')
        continue
    
    model_id = model[0]['id']
    
    # 检查是否已有 ACL
    existing = models.execute('app', uid, 'admin', 'ir.model.access', 'search',
        [('model_id', '=', model_id), ('group_id', '=', group_user_id)])
    
    if not existing:
        acl_id = models.execute('app', uid, 'admin', 'ir.model.access', 'create', {
            'name': f'{model_name}_user_read',
            'model_id': model_id,
            'group_id': group_user_id,
            'perm_read': True,
            'perm_write': False,
            'perm_create': False,
            'perm_unlink': False,
        })
        print(f'✓ 已添加 {model_name} 读取权限，ACL ID: {acl_id}')
    else:
        print(f'- {model_name} 已有权限')

print('\n完成!')
