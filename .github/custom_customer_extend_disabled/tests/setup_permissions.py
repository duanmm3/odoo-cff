#!/usr/bin/env python3
"""
使用 XML-RPC 手动设置权限规则
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def setup_permissions():
    print("=" * 60)
    print("设置权限规则...")
    print("=" * 60)
    
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    print(f"✓ 登录成功，UID: {uid}")
    
    # 获取模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    if not partner_model:
        print("✗ 找不到 res.partner 模型")
        return
    partner_model_id = partner_model[0]['id']
    print(f"✓ res.partner 模型ID: {partner_model_id}")
    
    # 获取组ID - 通过外部ID查找
    group_user_id = None
    group_admin_id = None
    
    # 查找 base.group_user
    group_user_ref = models.execute(DB, uid, PASSWORD, 'ir.model.data', 'search_read',
        [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
    if group_user_ref:
        group_user_id = group_user_ref[0]['res_id']
    
    # 查找 base.group_system
    group_admin_ref = models.execute(DB, uid, PASSWORD, 'ir.model.data', 'search_read',
        [('module', '=', 'base'), ('name', '=', 'group_system')], ['res_id'])
    if group_admin_ref:
        group_admin_id = group_admin_ref[0]['res_id']
    
    print(f"✓ group_user ID: {group_user_id}, group_admin ID: {group_admin_id}")
    
    # 删除旧规则
    old_rules = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search',
        [('model_id', '=', partner_model_id), ('name', 'in', ['res.partner: user filter', 'res.partner: admin all'])])
    if old_rules:
        models.execute(DB, uid, PASSWORD, 'ir.rule', 'unlink', old_rules)
        print(f"✓ 已删除旧规则: {old_rules}")
    
    # 创建普通用户规则
    user_rule_id = models.execute(DB, uid, PASSWORD, 'ir.rule', 'create', {
        'name': 'res.partner: user filter',
        'model_id': partner_model_id,
        'domain_force': "['|', ('create_uid', '=', user.id), ('shared_users', 'in', [user.id])]",
        'perm_read': True,
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': False,
        'active': True,
        'groups': [[4, group_user_id]] if group_user_id else [],
    })
    print(f"✓ 已创建普通用户规则，ID: {user_rule_id}")
    
    # 创建管理员规则
    admin_rule_id = models.execute(DB, uid, PASSWORD, 'ir.rule', 'create', {
        'name': 'res.partner: admin all',
        'model_id': partner_model_id,
        'domain_force': "[(1, '=', 1)]",
        'perm_read': True,
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': True,
        'active': True,
        'groups': [[4, group_admin_id]] if group_admin_id else [],
    })
    print(f"✓ 已创建管理员规则，ID: {admin_rule_id}")
    
    # 验证
    rules = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search_read',
        [('model_id', '=', partner_model_id), ('name', 'in', ['res.partner: user filter', 'res.partner: admin all'])],
        ['name', 'domain_force', 'perm_unlink', 'groups'])
    print(f"\n--- 当前规则 ---")
    for r in rules:
        print(f"  - {r['name']}: unlink={r['perm_unlink']}")
    
    print("\n=== 权限规则设置完成 ===")

if __name__ == "__main__":
    setup_permissions()
