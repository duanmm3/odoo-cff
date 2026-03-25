#!/usr/bin/env python3
"""检查 contacts 菜单使用的 action 和 view"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def check():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 查找 contacts 相关的 menu
    print("【查找 contacts 菜单】")
    menus = sock.execute_kw(DB, 2, 'admin', 'ir.ui.menu', 'search_read',
                          [[('name', 'ilike', 'contact')]],
                          {'fields': ['id', 'name', 'action', 'parent_path']})
    for m in menus:
        print(f"  菜单: {m['name']} (id={m['id']})")
        print(f"    action: {m.get('action')}")
    
    # 查找 contact 相关 action
    print("\n【查找 contacts 相关的 action】")
    actions = sock.execute_kw(DB, 2, 'admin', 'ir.actions.act_window', 'search_read',
                            [[('name', 'ilike', 'contact')]],
                            {'fields': ['id', 'name', 'res_model', 'domain', 'context']})
    for a in actions[:10]:
        print(f"  Action: {a['name']} (id={a['id']})")
        print(f"    res_model: {a.get('res_model')}")
        print(f"    domain: {a.get('domain')}")
        print(f"    context: {str(a.get('context'))[:100]}...")
    
    # 检查 res_partner 动作
    print("\n【查找 contact/action 中 res_model=res.partner 的】")
    partner_actions = sock.execute_kw(DB, 2, 'admin', 'ir.actions.act_window', 'search_read',
                                     [[('res_model', '=', 'res.partner')]],
                                     {'fields': ['id', 'name', 'domain', 'context']})
    for a in partner_actions:
        print(f"  Action: {a['name']} (id={a['id']})")
        if a.get('domain'):
            print(f"    domain: {a.get('domain')}")

if __name__ == '__main__':
    check()
