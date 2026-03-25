#!/usr/bin/env python3
"""contact_ext 数据库配置导入脚本 - 用于目标服务器"""

import xmlrpc.client as xmlrpclib

# ============================================================
# 请修改以下配置为你的目标服务器信息
# ============================================================
HOST = '目标服务器IP或域名'
PORT = 8069
DB = '数据库名称'
ADMIN_PASSWORD = 'admin密码'

def import_config():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    print("=" * 60)
    print("设置 contact_ext 相关配置")
    print("=" * 60)
    
    # 1. 设置系统参数 web.default_list_limit = 500
    print("\n【1. 设置系统参数】")
    existing = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                            [[('key', '=', 'web.default_list_limit')]],
                            {'fields': ['id']})
    
    if existing:
        sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'write', 
                      [[existing[0]['id']], {'value': '500'}])
        print("   ✓ web.default_list_limit = 500")
    else:
        sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'create',
                       [{'key': 'web.default_list_limit', 'value': '500'}])
        print("   ✓ web.default_list_limit = 500 (新建)")
    
    # 2. 设置 Action limits = 500
    print("\n【2. 设置 Action limits】")
    action_ids = [143, 343, 410, 440]
    for aid in action_ids:
        try:
            sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'write', [aid], {'limit': 500})
            print(f"   ✓ Action {aid} limit = 500")
        except Exception as e:
            print(f"   ✗ Action {aid} 失败: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("配置完成！")
    print("=" * 60)

if __name__ == '__main__':
    # 修改上面的 HOST, PORT, DB, ADMIN_PASSWORD 后运行
    print("请先修改脚本中的服务器配置信息！")
    print("HOST = '目标服务器IP'")
    print("PORT = 8069")
    print("DB = '数据库名称'")
    print("ADMIN_PASSWORD = 'admin密码'")
