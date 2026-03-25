#!/usr/bin/env python3
"""
查找 Alan 用户
"""

import xmlrpc.client

URL = "http://129.150.51.7:8070"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def find_alan():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    uid = common.authenticate(DB, USER, PASSWORD, {})
    
    # 搜索所有用户
    users = models.execute(DB, uid, PASSWORD, 'res.users', 'search_read',
        [], ['id', 'name', 'login'])
    
    print("=== 用户列表 ===")
    for u in users:
        print(f"  ID: {u['id']}, Name: {u['name']}, Login: {u['login']}")

if __name__ == "__main__":
    find_alan()
