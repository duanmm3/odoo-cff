#!/usr/bin/env python3
"""检查列表视图的 limit 设置"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 检查 list view (id=124) 的完整 arch
    print("【列表视图 (id=124)】")
    view = sock.execute(DB, 2, 'admin', 'ir.ui.view', 'read', [124], ['id', 'name', 'type', 'arch'])
    if view:
        arch = view[0].get('arch', '')
        print(f"arch_db (原始): {arch[:1000]}")
        
        # 检查是否有 limit 属性
        if 'limit' in arch:
            idx = arch.find('limit')
            print(f"\n包含 limit: ...{arch[max(0,idx-20):idx+50]}...")
        
    # 检查 kanban view
    print("\n【Kanban 视图 (id=129)】")
    view2 = sock.execute(DB, 2, 'admin', 'ir.ui.view', 'read', [129], ['id', 'name', 'arch'])
    if view2:
        arch = view2[0].get('arch', '')
        if 'limit' in arch:
            idx = arch.find('limit')
            print(f"包含 limit: ...{arch[max(0,idx-20):idx+50]}...")
        else:
            print("不包含 limit")
    
    # 检查 action 143 的完整配置
    print("\n【Action 143 完整配置】")
    action = sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'read', [143], 
                         ['id', 'name', 'domain', 'context', 'view_mode', 'limit', 'search_view_id'])
    print(f"Action: {action}")
    
    # 检查 action 343
    print("\n【Action 343 (有 my_contacts)】")
    action343 = sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'read', [343], 
                            ['id', 'name', 'domain', 'context', 'limit', 'search_view_id'])
    print(f"Action: {action343}")

if __name__ == '__main__':
    check()
