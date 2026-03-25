#!/usr/bin/env python3
"""
contact_ext 配置导入脚本 - 在目标服务器上运行

使用前请修改下面的配置信息：
- HOST: 服务器IP
- PORT: 端口 (通常 8069)
- DB: 数据库名称
- ADMIN_PASSWORD: admin密码
"""

import xmlrpc.client as xmlrpclib

# ============================================================
# 请修改以下配置为你的目标服务器信息
# ============================================================
HOST = 'localhost'          # 服务器IP或域名
PORT = 8069                # 端口
DB = 'app'                 # 数据库名称
ADMIN_PASSWORD = 'admin'   # admin密码

def import_config():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    print("=" * 60)
    print("contact_ext 配置导入")
    print(f"目标: {HOST}:{PORT}/{DB}")
    print("=" * 60)
    
    # 1. 设置系统参数 web.default_list_limit = 500
    print("\n【1. 系统参数】")
    try:
        existing = sock.execute_kw(DB, 2, ADMIN_PASSWORD, 'ir.config_parameter', 'search_read',
                                [[('key', '=', 'web.default_list_limit')]],
                                {'fields': ['id']})
        
        if existing:
            sock.execute_kw(DB, 2, ADMIN_PASSWORD, 'ir.config_parameter', 'write', 
                          [[existing[0]['id']], {'value': '500'}])
            print("   ✓ web.default_list_limit = 500 (已更新)")
        else:
            sock.execute_kw(DB, 2, ADMIN_PASSWORD, 'ir.config_parameter', 'create',
                           [{'key': 'web.default_list_limit', 'value': '500'}])
            print("   ✓ web.default_list_limit = 500 (已创建)")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
    
    # 2. 设置 Action limits = 500
    print("\n【2. Action limits】")
    action_ids = [143, 343, 410, 440]
    for aid in action_ids:
        try:
            sock.execute(DB, 2, ADMIN_PASSWORD, 'ir.actions.act_window', 'write', [aid], {'limit': 500})
            print(f"   ✓ Action {aid} limit = 500")
        except Exception as e:
            print(f"   ⚠ Action {aid}: {str(e)[:40]}")
    
    # 3. 验证 contact_ext 模块已安装
    print("\n【3. 验证模块】")
    try:
        modules = sock.execute_kw(DB, 2, ADMIN_PASSWORD, 'ir.module.module', 'search_read',
                                [[('name', '=', 'contact_ext')]],
                                {'fields': ['name', 'state']})
        if modules:
            print(f"   ✓ contact_ext 已安装: state={modules[0]['state']}")
        else:
            print("   ⚠ contact_ext 未安装，请先升级模块")
    except Exception as e:
        print(f"   ⚠ 验证失败: {e}")
    
    print("\n" + "=" * 60)
    print("配置完成！请刷新浏览器或重启 Odoo 服务。")
    print("=" * 60)

if __name__ == '__main__':
    import_config()
