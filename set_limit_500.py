#!/usr/bin/env python3
"""设置系统默认列表分页为 500"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def set_limit():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    print("=" * 60)
    print("设置列表分页为 500")
    print("=" * 60)
    
    # 1. 设置 web.default_list_limit
    print("\n【1. web.default_list_limit】")
    existing = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                            [[('key', '=', 'web.default_list_limit')]],
                            {'fields': ['id', 'key', 'value']})
    
    if existing:
        sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'write', 
                      [[existing[0]['id']], {'value': '500'}])
        print(f"   ✓ 已更新为: 500")
    else:
        sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'create',
                       [{'key': 'web.default_list_limit', 'value': '500'}])
        print(f"   ✓ 已创建: 500")
    
    # 2. 修改 Action 143 的 limit
    print("\n【2. Action 143 limit】")
    sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'write', [143], {'limit': 500})
    print(f"   ✓ 已设置为: 500")
    
    # 3. 修改 Action 410 (All Contacts)
    print("\n【3. Action 410 limit (All Contacts)】")
    sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'write', [410], {'limit': 500})
    print(f"   ✓ 已设置为: 500")
    
    # 4. 修改 Action 440 (Contacts)
    print("\n【4. Action 440 limit (Contacts)】")
    sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'write', [440], {'limit': 500})
    print(f"   ✓ 已设置为: 500")
    
    # 5. 修改 Action 343 (My Contacts)
    print("\n【5. Action 343 limit (My Contacts)】")
    sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'write', [343], {'limit': 500})
    print(f"   ✓ 已设置为: 500")
    
    print("\n" + "=" * 60)
    print("设置完成！请退出重新登录生效。")
    print("=" * 60)

if __name__ == '__main__':
    set_limit()
