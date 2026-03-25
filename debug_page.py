#!/usr/bin/env python3
"""完整模拟页面请求，调试 contacts API"""

import json
import requests

HOST = 'localhost'
PORT = 8069
DB = 'app'

def debug_page_request():
    session = requests.Session()
    
    # 1. 登录获取 session
    print("=" * 60)
    print("1. 登录 Crystal")
    print("=" * 60)
    
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
        user_info = result['result']
        print(f"✓ 登录成功: {user_info.get('name')}")
        print(f"  uid: {user_info.get('uid')}")
    else:
        print(f"✗ 登录失败: {result}")
        return
    
    # 2. 调用 contacts 的 web_search_read (和页面完全一样)
    print("\n" + "=" * 60)
    print("2. 调用 res.partner/web_search_read (页面同款)")
    print("=" * 60)
    
    # 这是页面调用的确切 API
    api_url = f'http://{HOST}:{PORT}/web/dataset/call_kw/res.partner/web_search_read'
    
    # 检查 cookie
    print(f"Session cookies: {dict(session.cookies)}")
    
    # 模拟页面请求
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
                    'display_name': {},
                },
                'domain': [],  # 空条件
                'offset': 0,
                'limit': 0,  # 0 表示不限
            }
        },
        'id': 2
    }
    
    response = session.post(api_url, json=api_data)
    print(f"API 响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'result' in data:
            result_data = data['result']
            records = result_data.get('records', [])
            length = result_data.get('length', 0)
            
            print(f"\n✓ API 返回结果:")
            print(f"  records 数量: {len(records)}")
            print(f"  length: {length}")
            
            # 检查第一条和最后一条
            if records:
                print(f"\n  第一条: id={records[0].get('id')}, name={records[0].get('display_name')}")
                if len(records) > 1:
                    print(f"  最后条: id={records[-1].get('id')}, name={records[-1].get('display_name')}")
        else:
            print(f"API 返回: {data}")
    else:
        print(f"API 错误: {response.text[:500]}")
    
    # 3. 检查服务器日志
    print("\n" + "=" * 60)
    print("3. 对比 XML-RPC 结果")
    print("=" * 60)
    
    import xmlrpc.client
    sock = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}/xmlrpc/2/object')
    
    crystal = sock.execute_kw(DB, 2, 'admin', 'res.users', 'search_read',
                             [[('login', '=', 'Crystal')]],
                             {'fields': ['id']})
    crystal_uid = crystal[0]['id']
    
    # search_count
    count = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'search_count', [])
    print(f"XML-RPC search_count: {count}")
    
    # search
    ids = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'search', [])
    print(f"XML-RPC search: {len(ids)} 条")
    
    # web_search_read
    web = sock.execute(DB, crystal_uid, 'Odoo123456', 'res.partner', 'web_search_read',
                     [], {'id': {}, 'display_name': {}}, 0, 0)
    print(f"XML-RPC web_search_read: {len(web.get('records', []))} 条")

if __name__ == '__main__':
    debug_page_request()
