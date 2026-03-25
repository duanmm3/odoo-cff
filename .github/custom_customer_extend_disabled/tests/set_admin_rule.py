#!/usr/bin/env python3
"""
设置管理员和用户过滤规则
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def set_admin_rule():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 获取 partner 模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    partner_model_id = partner_model[0]['id']
    
    # 获取组ID
    group_user_ref = models.execute(DB, uid, PASSWORD, 'ir.model.data', 'search_read',
        [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
    group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1
    
    group_admin_ref = models.execute(DB, uid, PASSWORD, 'ir.model.data', 'search_read',
        [('module', '=', 'base'), ('name', '=', 'group_system')], ['res_id'])
    group_admin_id = group_admin_ref[0]['res_id'] if group_admin_ref else 4
    
    # 删除旧规则
    old_rules = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search',
        [('model_id', '=', partner_model_id), ('name', 'in', ['res.partner: user filter', 'res.partner: admin rule'])])
    if old_rules:
        models.execute(DB, uid, PASSWORD, 'ir.rule', 'unlink', old_rules)
        print(f"已删除旧规则: {old_rules}")
    
    # 创建用户过滤规则
    user_rule_id = models.execute(DB, uid, PASSWORD, 'ir.rule', 'create', {
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
    print(f"✓ 已创建用户过滤规则，ID: {user_rule_id}")
    
    # 创建管理员规则 - 允许所有
    admin_rule_id = models.execute(DB, uid, PASSWORD, 'ir.rule', 'create', {
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
    print(f"✓ 已创建管理员规则，ID: {admin_rule_id}")

if __name__ == "__main__":
    set_admin_rule()
