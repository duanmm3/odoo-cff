#!/usr/bin/env python3
"""
检查 access control list
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def check_acls():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 获取模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    partner_model_id = partner_model[0]['id']
    
    # 获取ACL
    acls = models.execute(DB, uid, PASSWORD, 'ir.model.access', 'search_read',
        [('model_id', '=', partner_model_id)],
        ['name', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'])
    
    print("=== res.partner Access Control Lists ===")
    for a in acls:
        print(f"\nACL: {a['name']}")
        print(f"  group_id: {a['group_id']}")
        print(f"  permissions: read={a['perm_read']}, write={a['perm_write']}, create={a['perm_create']}, unlink={a['perm_unlink']}")

if __name__ == "__main__":
    check_acls()
