#!/usr/bin/env python3
"""导出 contact_ext 相关的数据库配置"""

import xmlrpc.client as xmlrpclib

HOST = 'localhost'
PORT = 8069
DB = 'app'

def export_config():
    sock = xmlrpclib.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    print("#" * 60)
    print("# contact_ext 数据库配置导出")
    print("#" * 60)
    
    print("\n# 1. 系统参数 (ir.config_parameter)")
    params = sock.execute_kw(DB, 2, 'admin', 'ir.config_parameter', 'search_read',
                          [[('key', '=', 'web.default_list_limit')]],
                          {'fields': ['key', 'value']})
    for p in params:
        print(f"#   {p['key']} = {p['value']}")
    
    print("\n# 2. Action 设置 (ir.actions.act_window)")
    action_ids = [143, 343, 410, 440]
    for aid in action_ids:
        try:
            action = sock.execute(DB, 2, 'admin', 'ir.actions.act_window', 'read', 
                               [aid], ['id', 'name', 'limit'])
            if action:
                print(f"#   Action {aid} ({action[0]['name']}): limit={action[0]['limit']}")
        except:
            pass
    
    print("\n# 3. res_partner 权限规则 (ir.rule)")
    rules = sock.execute_kw(DB, 2, 'admin', 'ir.rule', 'search_read',
                          [[('model_id.model', '=', 'res.partner')]],
                          {'fields': ['id', 'name', 'domain_force', 'groups']})
    for r in rules:
        print(f"#   Rule {r['id']}: {r['name']}")
        print(f"#     domain_force: {r['domain_force']}")
        print(f"#     groups: {r['groups']}")
    
    print("\n" + "#" * 60)
    print("# 请在目标服务器上执行以下脚本设置配置")
    print("#" * 60)

if __name__ == '__main__':
    export_config()
