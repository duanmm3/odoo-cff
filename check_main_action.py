#!/usr/bin/env python3
"""检查 contacts 菜单 id=111 使用的 action"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 主 Contacts 菜单 (id=111) 使用的 action
    print("【主 Contacts 菜单 (id=111)】")
    menu = sock.execute(DB, 2, 'admin', 'ir.ui.menu', 'read', [111], ['id', 'name', 'action'])
    print(f"菜单: {menu}")
    
    # 读取 action 详情
    action_id = 143  # Contacts 菜单使用的 action
    print(f"\n【Action id={action_id}】")
    action = sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'read', [action_id], 
                         ['id', 'name', 'res_model', 'domain', 'context', 'view_mode', 'target'])
    print(f"Action: {action}")
    
    # 检查 view_ids
    print(f"\n【Action 的 view_ids】")
    view_ids = sock.execute_kw(DB, 2, 'admin', 'ir.actions.act_window.view', 'search_read',
                              [[('act_window_id', '=', action_id)]],
                              {'fields': ['id', 'view_mode', 'view_id']})
    for v in view_ids:
        print(f"  view: mode={v['view_mode']}, id={v['view_id']}")
    
    # 检查 view 的 arch
    if view_ids:
        view_id = view_ids[0]['view_id'][0] if isinstance(view_ids[0]['view_id'], list) else view_ids[0]['view_id']
        view = sock.execute(DB, 2, 'admin', 'ir.ui.view', 'read', [view_id], ['id', 'name', 'type', 'arch'])
        if view:
            arch = view[0].get('arch', '')
            print(f"\n【View arch (前500字符)】")
            print(arch[:500])

if __name__ == '__main__':
    check()
