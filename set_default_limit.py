#!/usr/bin/env python3
"""设置系统默认列表分页为 50"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def set_default_limit():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    print("=" * 60)
    print("设置系统默认列表分页为 50")
    print("=" * 60)
    
    # 1. 检查是否已存在该参数
    print("\n【1. 检查现有参数】")
    existing = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                            [[('key', '=', 'web.default_list_limit')]],
                            {'fields': ['id', 'key', 'value']})
    
    if existing:
        print(f"   现有值: {existing[0]['value']}")
        param_id = existing[0]['id']
        # 更新
        sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'write', 
                      [[param_id], {'value': '50'}])
        print(f"   ✓ 已更新为: 50")
    else:
        # 创建新参数
        print("   参数不存在，创建中...")
        new_id = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'create',
                               [{'key': 'web.default_list_limit', 'value': '50'}])
        print(f"   ✓ 已创建，ID: {new_id}")
    
    # 2. 验证设置
    print("\n【2. 验证设置】")
    params = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                          [[('key', '=', 'web.default_list_limit')]],
                          {'fields': ['key', 'value']})
    if params:
        print(f"   ✓ web.default_list_limit = {params[0]['value']}")
    
    # 3. 同时修改 Action 143 的 limit
    print("\n【3. 修改 Action 143 的 limit】")
    action = sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'write', 
                        [143], {'limit': 50})
    print(f"   ✓ Action 143 limit 已设置为 50")
    
    print("\n" + "=" * 60)
    print("设置完成！")
    print("请用户重新登录或刷新页面生效。")
    print("=" * 60)

if __name__ == '__main__':
    set_default_limit()
