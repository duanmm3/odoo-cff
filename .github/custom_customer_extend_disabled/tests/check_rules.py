#!/usr/bin/env python3
"""
检查并修复权限规则
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def check_rules():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 获取 partner 模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    partner_model_id = partner_model[0]['id']
    
    # 获取 Alan 的用户信息
    alan = models.execute(DB, uid, PASSWORD, 'res.users', 'search_read',
        [('login', '=', 'Alan')], ['id', 'name', 'login'])
    print(f"Alan: {alan}")
    
    # 检查所有规则
    rules = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search_read', 
        [('model_id', '=', partner_model_id)],
        ['name', 'domain_force', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink', 'global', 'groups'])
    
    print("\n=== res.partner 所有规则 ===")
    for r in rules:
        print(f"\n规则: {r['name']}")
        print(f"  global: {r['global']}")
        print(f"  权限: read={r['perm_read']}, write={r['perm_write']}, create={r['perm_create']}, unlink={r['perm_unlink']}")
        print(f"  domain: {r['domain_force'][:80] if r.get('domain_force') else 'N/A'}...")
        print(f"  groups: {r.get('groups')}")

if __name__ == "__main__":
    check_rules()
