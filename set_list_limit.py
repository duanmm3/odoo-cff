#!/usr/bin/env python3
"""设置系统默认列表分页大小"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def set_default_limit():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 检查现有的系统参数
    print("【检查现有系统参数】")
    params = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                           [[('key', 'ilike', 'list')]],
                           {'fields': ['id', 'key', 'value']})
    for p in params:
        print(f"  {p['key']} = {p['value']}")
    
    # 检查是否有 web 相关参数
    print("\n【检查 web.list.* 参数】")
    web_params = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                                [[('key', 'ilike', 'web.')]],
                                {'fields': ['id', 'key', 'value']})
    for p in web_params[:10]:
        print(f"  {p['key']} = {p['value']}")
    
    # 检查 action 143 的 limit
    print("\n【检查 Action 143 的 limit】")
    action = sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'read', [143], ['id', 'name', 'limit'])
    print(f"  Action 143 limit: {action[0]['limit']}")

if __name__ == '__main__':
    set_default_limit()
