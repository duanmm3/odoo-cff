#!/usr/bin/env python3
"""检查 Crystal 用户的特殊设置"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check_crystal():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 获取 Crystal 用户信息
    crystal = sock.execute_kw(DB, 2, 'admin', 'res.users', 'search_read',
                             [[('login', '=', 'Crystal')]],
                             {'fields': ['id', 'login', 'name', 'active']})
    
    if not crystal:
        print("未找到 Crystal 用户")
        return
    
    c = crystal[0]
    print("=" * 60)
    print(f"Crystal 用户信息:")
    print(f"  id: {c['id']}")
    print(f"  name: {c['name']}")
    print(f"  login: {c['login']}")
    print(f"  active: {c['active']}")
    print("=" * 60)
    
    crystal_uid = c['id']
    
    # 检查 ir.rule 权限规则
    print("\n【检查 ir.rule 权限规则 for res.partner】")
    rules = sock.execute_kw(DB, 2, 'admin', 'ir.rule', 'search_read',
                           [[['model_id.model', '=', 'res.partner']]],
                           {'fields': ['id', 'name', 'domain_force', 'groups', 'perm_read']})
    
    for rule in rules:
        print(f"\n规则: {rule['name']} (id={rule['id']})")
        print(f"  domain_force: {rule.get('domain_force', 'N/A')}")
        print(f"  groups: {rule.get('groups', [])}")
        print(f"  perm_read: {rule.get('perm_read', False)}")
    
    # 检查 ACL 权限
    print("\n【检查 ACL 权限 for res.partner】")
    acls = sock.execute_kw(DB, 2, 'admin', 'ir.model.access', 'search_read',
                          [[['model_id.model', '=', 'res.partner']]],
                          {'fields': ['id', 'name', 'group_id', 'perm_read', 'perm_write']})
    
    for acl in acls:
        print(f"  {acl['name']}: read={acl['perm_read']}, write={acl['perm_write']}, group={acl['group_id']}")
    
    # Crystal 可见联系人
    print("\n【Crystal 可见联系人】")
    count = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'search_count', [])
    print(f"  search_count: {count}")
    
    ids = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'search', [])
    print(f"  search: {len(ids)} 条")
    
    # 检查 shared_users 数据
    print("\n【检查 shared_users 数据】")
    shared_count = sock.execute_kw(DB, 2, 'admin', 'res.partner', 'search_count',
                                  [[('shared_users', 'in', [crystal_uid])]])
    print(f"  shared_users 包含 Crystal: {shared_count}")
    
    # 检查是否有联系人属于 Crystal
    created_count = sock.execute_kw(DB, 2, 'admin', 'res.partner', 'search_count',
                                   [[('create_uid', '=', crystal_uid)]])
    print(f"  create_uid = Crystal: {created_count}")
    
    # 检查 Crystal 属于哪些组
    print("\n【检查 Crystal 属于的组】")
    all_groups = sock.execute_kw(DB, 2, 'admin', 'res.groups', 'search_read',
                                 [[('share', '=', False)]],
                                 {'fields': ['id', 'name', 'users'], 'limit': 100})
    
    for g in all_groups:
        users = g.get('users', [])
        if crystal_uid in [u[0] if isinstance(u, list) else u for u in users]:
            print(f"  Crystal 在组: {g['name']} (id={g['id']})")

if __name__ == '__main__':
    check_crystal()
