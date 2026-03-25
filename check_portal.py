#!/usr/bin/env python3
"""检查 Crystal 是否在 Portal/Public 组"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    crystal_uid = 28
    
    # 检查 Portal 组 (id=10)
    portal = sock.execute_kw(DB, 2, 'admin', 'res.partner', 'search_read',
                            [[('id', 'in', [10, 11])]],
                            {'fields': ['id', 'name']})
    print(f"Portal/Public 组: {portal}")
    
    # 检查 res_groups 表
    groups = sock.execute_kw(DB, 2, 'admin', 'res.groups', 'search_read',
                           [[('id', 'in', [10, 11])]],
                           {'fields': ['id', 'name']})
    print(f"\n组信息: {groups}")
    
    # 直接查数据库
    print("\n【直接查询组用户关系】")
    sock.execute_kw(DB, 2, 'admin', 'execute_kw', [
        'res.groups', 'read', [[10, 11]], ['id', 'name']
    ])
    
    # 另一种方式 - 查 res_users_res_groups_rel
    import xmlrpc.client
    sock2 = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 检查用户属于哪些组ID
    user_data = sock2.execute(DB, 2, 'admin', 'res.users', 'read', [crystal_uid], ['id', 'name'])
    print(f"\n用户数据: {user_data}")
    
    # 检查 user_ids 字段
    user_with_groups = sock2.execute(DB, 2, 'admin', 'res.groups', 'search_read',
                                     [[('users', 'in', [crystal_uid])]],
                                     {'fields': ['id', 'name']})
    print(f"\n用户 Crystal 属于的组:")
    for g in user_with_groups:
        print(f"  - {g['name']} (id={g['id']})")

if __name__ == '__main__':
    check()
