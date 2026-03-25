#!/usr/bin/env python3
"""
设置数据过滤规则 - 只显示自己创建或共享的联系人
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 获取模型和组
partner_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read', 
    [('model', '=', 'res.partner')], ['id'])
partner_model_id = partner_model[0]['id']

group_user_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1

group_admin_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_system')], ['res_id'])
group_admin_id = group_admin_ref[0]['res_id'] if group_admin_ref else 4

# 创建用户过滤规则
user_rule_id = models.execute('app', uid, 'admin', 'ir.rule', 'create', {
    'name': 'res.partner: user filter',
    'model_id': partner_model_id,
    'domain_force': "['|', ('create_uid', '=', user.id), ('shared_users', 'in', [user.id])]",
    'perm_read': True,
    'perm_write': True,
    'perm_create': True,
    'perm_unlink': False,
    'active': True,
    'groups': [[4, group_user_id]],
})
print(f'✓ 已创建用户过滤规则，ID: {user_rule_id}')

# 创建管理员规则 - 允许所有
admin_rule_id = models.execute('app', uid, 'admin', 'ir.rule', 'create', {
    'name': 'res.partner: admin rule',
    'model_id': partner_model_id,
    'domain_force': "[(1, '=', 1)]",
    'perm_read': True,
    'perm_write': True,
    'perm_create': True,
    'perm_unlink': True,
    'active': True,
    'groups': [[4, group_admin_id]],
})
print(f'✓ 已创建管理员规则，ID: {admin_rule_id}')

print('\n完成!')
