#!/usr/bin/env python3
"""
修改全局规则 - 允许所有用户访问所有联系人
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def modify_global_rule():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 获取 partner 模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    partner_model_id = partner_model[0]['id']
    
    # 查找全局规则
    global_rule = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search',
        [('model_id', '=', partner_model_id), ('global', '=', True), ('name', '=', 'res.partner company')])
    
    if global_rule:
        # 修改全局规则，允许所有
        models.execute(DB, uid, PASSWORD, 'ir.rule', 'write', global_rule, {
            'domain_force': "[(1, '=', 1)]"
        })
        print(f"✓ 已修改全局规则: {global_rule}")
    else:
        print("未找到全局规则")

if __name__ == "__main__":
    modify_global_rule()
