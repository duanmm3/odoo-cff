#!/usr/bin/env python3
"""
添加 bus 相关权限
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取 group_user ID
group_user_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1

# 尝试获取 bus 相关模型
bus_models = ['bus.presence', 'bus.channel']

print("=== 添加 Bus 权限 ===")

for model_name in bus_models:
    try:
        model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
            [('model', '=', model_name)], ['id'])
        if model:
            model_id = model[0]['id']
            
            existing = models.execute('app', uid, 'admin', 'ir.model.access', 'search',
                [('model_id', '=', model_id), ('group_id', '=', group_user_id)])
            
            if not existing:
                acl_id = models.execute('app', uid, 'admin', 'ir.model.access', 'create', {
                    'name': f'{model_name}_user',
                    'model_id': model_id,
                    'group_id': group_user_id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True,
                })
                print(f"✓ {model_name}: ACL 已创建")
            else:
                print(f"- {model_name}: 已存在")
    except Exception as e:
        print(f"✗ {model_name}: {str(e)[:40]}")

print("\n完成!")
