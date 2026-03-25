#!/usr/bin/env python3
"""检查 contacts 页面使用的 action 和 searchview"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 检查所有 Contacts 相关的 action
    print("【所有 Contacts actions】")
    actions = sock.execute_kw(DB, 2, 'admin', 'ir.actions.act_window', 'search_read',
                            [[('res_model', '=', 'res.partner'), ('name', 'ilike', 'Contact')]],
                            {'fields': ['id', 'name', 'domain', 'context']})
    for a in actions:
        print(f"\nAction: {a['name']} (id={a['id']})")
        print(f"  domain: {a.get('domain')}")
        print(f"  context: {a.get('context')}")
    
    # 检查是否有 search_default 过滤器
    print("\n\n【检查 search_default_my_contacts 过滤器】")
    search_views = sock.execute_kw(DB, 2, 'admin', 'ir.ui.view', 'search_read',
                                  [[('model', '=', 'res.partner'), ('type', '=', 'search')]],
                                  {'fields': ['id', 'name', 'arch']})
    for sv in search_views[:3]:
        print(f"\nSearch View: {sv['name']} (id={sv['id']})")
        arch = sv.get('arch', '')
        if 'my_contacts' in arch:
            print("  包含 my_contacts 过滤器")
            # 找到相关部分
            idx = arch.find('my_contacts')
            print(f"  上下文: {arch[max(0,idx-100):idx+200]}")

if __name__ == '__main__':
    check()
