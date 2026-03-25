#!/usr/bin/env python3
"""对比 Sunny 和 Crystal 的页面 API"""

import json
import requests

HOST = 'localhost'
PORT = 8069
DB = 'app'

def test():
    # 测试 Crystal
    print("=" * 60)
    print("Crystal (uid=28)")
    print("=" * 60)
    
    session = requests.Session()
    
    # 登录
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
    session.post(auth_url, json=auth_data)
    
    # 调用 web_search_read (空 domain = 不过滤)
    api_url = f'http://{HOST}:{PORT}/web/dataset/call_kw/res.partner/web_search_read'
    api_data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'model': 'res.partner',
            'method': 'web_search_read',
            'args': [],
            'kwargs': {
                'specification': {'id': {}},
                'domain': [],
                'offset': 0,
                'limit': 0,
            }
        },
        'id': 2
    }
    
    resp = session.post(api_url, json=api_data)
    if resp.status_code == 200:
        data = resp.json()
        records = data['result'].get('records', [])
        length = data['result'].get('length', 0)
        print(f"API 返回: {len(records)} records, length={length}")
    
    # 测试 Sunny
    print("\n" + "=" * 60)
    print("Sunny (uid=31)")
    print("=" * 60)
    
    session2 = requests.Session()
    auth_data['params']['login'] = 'Sunny'
    session2.post(auth_url, json=auth_data)
    
    resp2 = session2.post(api_url, json=api_data)
    if resp2.status_code == 200:
        data2 = resp2.json()
        records2 = data2['result'].get('records', [])
        length2 = data2['result'].get('length', 0)
        print(f"API 返回: {len(records2)} records, length={length2}")
    
    # XML-RPC 对比
    print("\n" + "=" * 60)
    print("XML-RPC 对比")
    print("=" * 60)
    
    import xmlrpc.client
    sock = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    crystal_count = sock.execute(DB, 28, 'Odoo123456', 'res.partner', 'search_count', [])
    sunny_count = sock.execute(DB, 31, 'Odoo123456', 'res.partner', 'search_count', [])
    
    print(f"Crystal XML-RPC search_count: {crystal_count}")
    print(f"Sunny XML-RPC search_count: {sunny_count}")

if __name__ == '__main__':
    test()
