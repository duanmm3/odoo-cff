#!/usr/bin/env python3
"""测试页面 API 请求"""

import json
import requests

HOST = 'localhost'
PORT = 8069
DB = 'app'

def test_page_api():
    session = requests.Session()
    
    # 1. 登录 Crystal
    print("1. 登录 Crystal")
    auth_url = f'http://{HOST}:{PORT}/web/session/authenticate'
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
    
    response = session.post(auth_url, json=auth_data)
    result = response.json()
    
    if 'result' in result and result['result']:
        print(f"   ✓ 登录成功: {result['result'].get('name')}")
    else:
        print(f"   ✗ 登录失败")
        return
    
    # 2. 调用 web_search_read (和页面完全一样的方式)
    print("\n2. 调用 res.partner/web_search_read")
    api_url = f'http://{HOST}:{PORT}/web/dataset/call_kw/res.partner/web_search_read'
    
    # 模拟页面请求 - 使用空 limit 表示不限
    api_data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'model': 'res.partner',
            'method': 'web_search_read',
            'args': [],  # 空 domain
            'kwargs': {
                'specification': {
                    'id': {},
                },
                'domain': [],  # 空条件 - 不过滤
                'offset': 0,
                'limit': 0,  # 0 = 不限制
            }
        },
        'id': 2
    }
    
    response = session.post(api_url, json=api_data)
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            records = data['result'].get('records', [])
            length = data['result'].get('length', 0)
            
            print(f"   ✓ API 返回:")
            print(f"     records 数量: {len(records)}")
            print(f"     length: {length}")
            
            if length > 80:
                print(f"\n   ⚠️ API 返回 {length} 条，但页面只显示 80 条")
                print(f"   原因: Action 设置了 limit=80")
    
    # 3. 对比 XML-RPC
    print("\n3. XML-RPC 对比")
    import xmlrpc.client
    sock = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    count = sock.execute(DB, 28, 'Odoo123456', 'res.partner', 'search_count', [])
    print(f"   search_count: {count}")

if __name__ == '__main__':
    test_page_api()
