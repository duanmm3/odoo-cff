#!/usr/bin/env python3
"""检查用户收藏的视图设置"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    crystal_uid = 28
    
    # 检查用户设置
    print("【检查 Crystal 的用户设置 (ir.ui.menu.sc)】")
    settings = sock.execute_kw(DB, 2, 'admin', 'ir.ui.menu.sc', 'search_read',
                             [[('user_id', '=', crystal_uid)]],
                             {'fields': ['id', 'menu_id', 'user_id']})
    print(f"收藏的菜单数量: {len(settings)}")
    
    for s in settings[:10]:
        print(f"  menu_id={s['menu_id']}")
    
    # 检查 action 143 的完整配置
    print("\n【检查 action 143 是否是主 Contacts 菜单】")
    menus = sock.execute_kw(DB, 2, 'admin', 'ir.ui.menu', 'search_read',
                          [[('action', '=', 'ir.actions.act_window,143')]],
                          {'fields': ['id', 'name', 'action']})
    for m in menus:
        print(f"  菜单: {m['name']} (id={m['id']})")
    
    # 检查 Crystal 属于哪些组
    print("\n【检查 Crystal 属于的组】")
    groups = sock.execute_kw(DB, 2, 'admin', 'res.groups', 'search_read',
                           [[('share', '=', True)]],
                           {'fields': ['id', 'name']})
    
    # 检查 res_users_res_groups_rel 表
    for g in groups[:10]:
        group_id = g['id']
        # 直接用 search with user_id domain
        pass
    
    # 另一种方式：检查 res_users 表
    print("\n【直接读取 Crystal 用户数据】")
    user = sock.execute(DB, 2, 'admin', 'res.users', 'read', [crystal_uid], ['id', 'name', 'login'])
    print(f"用户: {user}")

if __name__ == '__main__':
    check()
