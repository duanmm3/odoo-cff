#!/usr/bin/env python3
"""
修复权限 - 确保普通用户可以访问联系人列表
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def fix_permissions():
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
    
    # 删除过滤规则，改为允许所有
    old_rules = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search',
        [('model_id', '=', partner_model_id), ('name', '=', 'res.partner: user filter')])
    if old_rules:
        models.execute(DB, uid, PASSWORD, 'ir.rule', 'unlink', old_rules)
        print(f"已删除过滤规则: {old_rules}")
    
    # 创建新规则 - 允许所有用户查看所有联系人
    rule_id = models.execute(DB, uid, PASSWORD, 'ir.rule', 'create', {
        'name': 'res.partner: all access',
        'model_id': partner_model_id,
        'domain_force': "[(1, '=', 1)]",
        'perm_read': True,
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': False,
        'active': True,
        'groups': [[4, group_user_id]],
    })
    print(f"✓ 已创建访问规则，ID: {rule_id}")

if __name__ == "__main__":
    fix_permissions()
