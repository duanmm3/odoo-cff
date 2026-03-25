#!/usr/bin/env python3
"""
删除自定义规则，测试基础权限
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def cleanup_rules():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 获取 partner 模型ID
    partner_model = models.execute(DB, uid, PASSWORD, 'ir.model', 'search_read', 
        [('model', '=', 'res.partner')], ['id'])
    partner_model_id = partner_model[0]['id']
    
    # 删除自定义规则
    rules = models.execute(DB, uid, PASSWORD, 'ir.rule', 'search',
        [('model_id', '=', partner_model_id), ('name', 'in', ['res.partner: user filter', 'res.partner: admin all'])])
    
    if rules:
        models.execute(DB, uid, PASSWORD, 'ir.rule', 'unlink', rules)
        print(f"已删除规则: {rules}")
    else:
        print("没有找到自定义规则")

if __name__ == "__main__":
    cleanup_rules()
