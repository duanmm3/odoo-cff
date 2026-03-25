#!/usr/bin/env python3
"""
添加 ir.actions.act_window 的访问权限
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8070'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取模型ID
action_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read',
    [('model', '=', 'ir.actions.act_window')], ['id'])
action_model_id = action_model[0]['id']

# 获取 group_user ID
group_user_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1

# 创建 ACL
acl_id = models.execute('app', uid, 'admin', 'ir.model.access', 'create', {
    'name': 'action_window_user_access',
    'model_id': action_model_id,
    'group_id': group_user_id,
    'perm_read': True,
    'perm_write': False,
    'perm_create': False,
    'perm_unlink': False,
})
print(f'✓ 已创建 ACL，ID: {acl_id}')
