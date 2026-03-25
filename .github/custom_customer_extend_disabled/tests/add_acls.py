#!/usr/bin/env python3
"""
添加访问控制列表
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def add_acls():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 获取模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    partner_model_id = partner_model[0]['id']
    
    # 获取 group_user ID (base.group_user)
    group_user_ref = models.execute(DB, uid, PASSWORD, 'ir.model.data', 'search_read',
        [('module', '=', 'base'), ('name', '=', 'group_user')], ['res_id'])
    group_user_id = group_user_ref[0]['res_id'] if group_user_ref else 1
    
    # 删除旧的ACL (如果有)
    old_acls = models.execute(DB, uid, PASSWORD, 'ir.model.access', 'search',
        [('name', '=', 'access_res_partner_user_full')])
    if old_acls:
        models.execute(DB, uid, PASSWORD, 'ir.model.access', 'unlink', old_acls)
        print("已删除旧ACL")
    
    # 创建新ACL - 给予完整权限
    acl_id = models.execute(DB, uid, PASSWORD, 'ir.model.access', 'create', {
        'name': 'access_res_partner_user_full',
        'model_id': partner_model_id,
        'group_id': group_user_id,
        'perm_read': True,
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': False,
    })
    print(f"✓ 已创建ACL，ID: {acl_id}")

if __name__ == "__main__":
    add_acls()
