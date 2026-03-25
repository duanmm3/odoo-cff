#!/usr/bin/env python3
"""模拟页面请求，测试 contacts 列表 API"""

import json
import requests

HOST = 'localhost'
PORT = 8069
DB = 'app'

def test_page_api():
    # 先登录获取 session
    session = requests.Session()
    
    # 1. 获取登录页面（获取 csrf token）
    login_url = f'http://{HOST}:{PORT}/web/login'
    response = session.get(login_url)
    print(f"Login page status: {response.status_code}")
    
    # 2. 登录
    # 从页面提取 csrf token
    csrf_token = session.cookies.get('csrf_token') or 'demo'
    
    login_data = {
        'login': 'Crystal',
        'password': 'Odoo123456',
        'csrf_token': csrf_token,
    }
    
    # 尝试通过 JSON-RPC 登录
    json_url = f'http://{HOST}:{PORT}/web/session/authenticate'
    auth_data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'db': DB,
            'login': 'Crystal',
            'password': 'Odoo123456',
        },
        'id': 1
    }
    
    response = session.post(json_url, json=auth_data)
    print(f"Auth response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'result' in result and result['result']:
            print(f"登录成功: {result['result'].get('name', 'N/A')}")
            
            # 3. 调用 contacts 列表的 API
            contacts_url = f'http://{HOST}:{PORT}/web/dataset/call_kw/res.partner/web_search_read'
            
            contacts_data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'model': 'res.partner',
                    'method': 'web_search_read',
                    'args': [[], {'id': {}, 'display_name': {}}],
                    'kwargs': {
                        'offset': 0,
                        'limit': 0,
                    }
                },
                'id': 2
            }
            
            resp = session.post(contacts_url, json=contacts_data)
            print(f"Contacts API status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                if 'result' in data:
                    records = data['result'].get('records', [])
                    length = data['result'].get('length', 0)
                    print(f"API 返回: {len(records)} 条记录, length={length}")
                else:
                    print(f"API 返回: {data}")
    
    # 4. 直接用 XML-RPC 测试
    print("\n【对比 XML-RPC 测试】")
    import xmlrpc.client
    sock = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    # 查找 Crystal 用户
    crystal = sock.execute_kw(DB, 2, 'admin', 'res.users', 'search_read',
                             [[('login', '=', 'Crystal')]],
                             {'fields': ['id']})
    crystal_uid = crystal[0]['id'] if crystal else None
    
    if crystal_uid:
        count = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'search_count', [])
        print(f"XML-RPC search_count: {count}")
        
        ids = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'search', [])
        print(f"XML-RPC search: {len(ids)} 条")
        
        web_result = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'web_search_read',
                                [], {'id': {}}, 0, 0)
        print(f"XML-RPC web_search_read: {len(web_result.get('records', []))} 条")

if __name__ == '__main__':
    test_page_api()
