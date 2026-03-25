#!/usr/bin/env python3
"""
完整修复：确保普通用户可以访问联系人
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

print("=== 开始修复 ===")

# 1. 获取模型ID
partner_model = models.execute('app', uid, 'admin', 'ir.model', 'search_read', 
    [('model', '=', 'res.partner')], ['id'])
partner_model_id = partner_model[0]['id']

# 2. 获取组ID
group_user_ref = models.execute('app', uid, 'admin', 'ir.model.data', 'search_read',
    [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1

# 3. 删除之前的过滤规则
old_rules = models.execute('app', uid, 'admin', 'ir.rule', 'search',
    [('model_id', '=', partner_model_id), ('name', 'in', ['res.partner: user filter', 'res.partner: admin rule'])])
if old_rules:
    models.execute('app', uid, 'admin', 'ir.rule', 'unlink', old_rules)
    print(f"✓ 已删除旧规则: {old_rules}")

# 4. 修改全局规则 - 允许所有
global_rule = models.execute('app', uid, 'admin', 'ir.rule', 'search',
    [('model_id', '=', partner_model_id), ('global', '=', True)])
if global_rule:
    models.execute('app', uid, 'admin', 'ir.rule', 'write', global_rule, {
        'domain_force': "[(1, '=', 1)]"
    })
    print("✓ 已修改全局规则")

# 5. 确保 ACL 存在
existing_acl = models.execute('app', uid, 'admin', 'ir.model.access', 'search',
    [('name', '=', 'res.partner_user_access'), ('model_id', '=', partner_model_id)])

if not existing_acl:
    acl_id = models.execute('app', uid, 'admin', 'ir.model.access', 'create', {
        'name': 'res.partner_user_access',
        'model_id': partner_model_id,
        'group_id': group_user_id,
        'perm_read': True,
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': False,
    })
    print(f"✓ 已创建 ACL: {acl_id}")
else:
    print("- ACL 已存在")

# 6. 禁用有问题的视图
views = models.execute('app', uid, 'admin', 'ir.ui.view', 'search',
    [('model', '=', 'res.partner'), ('type', '=', 'list'), ('name', 'like', 'custom'), ('active', '=', True)])
if views:
    models.execute('app', uid, 'admin', 'ir.ui.view', 'write', views, {'active': False})
    print(f"✓ 已禁用 {len(views)} 个自定义视图")

print("\n=== 测试 Amanda ===")
amanda_uid = common.authenticate('app', 'Amanda', 'Odoo123456', {})
partners = models.execute('app', amanda_uid, 'Odoo123456', 'res.partner', 'search_read', 
    [], ['name'], 0, 10)
print(f"Amanda 可见联系人: {len(partners)}")
for p in partners[:5]:
    print(f"  - {p['name']}")

print("\n=== 完成 ===")
