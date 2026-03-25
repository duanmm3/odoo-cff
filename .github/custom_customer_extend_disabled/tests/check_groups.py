#!/usr/bin/env python3
"""
测试删除权限 - 检查用户属于哪个组
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "Amanda"
PASSWORD = "Odoo123456"

def check_user_groups():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    print(f"Amanda UID: {uid}")
    
    # 获取用户组
    user = models.execute(DB, uid, PASSWORD, 'res.users', 'search_read',
        [('id', '=', uid)], ['name', 'groups_id'])
    if user:
        print(f"用户: {user[0]['name']}")
        print(f"组: {user[0]['groups_id']}")
        
        # 获取组名
        if user[0]['groups_id']:
            groups = models.execute(DB, uid, PASSWORD, 'res.groups', 'search_read',
                [('id', 'in', user[0]['groups_id'])], ['name'])
            print("组名称:")
            for g in groups:
                print(f"  - {g['name']}")

if __name__ == "__main__":
    check_user_groups()
