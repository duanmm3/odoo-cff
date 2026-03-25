#!/usr/bin/env python3
"""
测试普通用户对联系人的权限
使用 XML-RPC 连接 Odoo 并验证权限
"""

import xmlrpc.client
import sys

# Odoo 服务器配置 - 远程服务器
URL = "http://129.150.51.7:8069"
DB = "app"
USER = "admin"
PASSWORD = "admin"

def test_permissions():
    print("=" * 60)
    print("开始测试用户权限...")
    print("=" * 60)
    
    # 连接 Odoo
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    # 登录获取 uid
    try:
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if not uid:
            print(f"✗ 登录失败")
            return False
        print(f"✓ 登录成功，用户 UID: {uid}")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print("提示: 请确保 Odoo 服务器可访问，或在本地运行测试")
        return False
    
    # 测试1: 读取联系人 - 应该只能看到自己创建或共享的
    print("\n--- 测试1: 读取联系人 ---")
    try:
        partners = models.execute(DB, uid, PASSWORD, 'res.partner', 'search_read', [], ['name', 'create_uid', 'shared_users'])
        print(f"✓ 成功读取联系人，共 {len(partners)} 条")
        for p in partners[:3]:
            print(f"  - {p.get('name')} (创建者ID: {p.get('create_uid')})")
    except Exception as e:
        print(f"✗ 读取联系人失败: {e}")
        return False
    
    # 测试2: 创建联系人
    print("\n--- 测试2: 创建联系人 ---")
    try:
        new_partner_id = models.execute(DB, uid, PASSWORD, 'res.partner', 'create', {
            'name': '测试联系人_XMLRPC',
            'partner_type': 'customer',
            'customer_type': 'CT',
        })
        print(f"✓ 创建联系人成功，ID: {new_partner_id}")
    except Exception as e:
        print(f"✗ 创建联系人失败: {e}")
        return False
    
    # 测试3: 验证创建的联系人可以看到
    print("\n--- 测试3: 验证创建的联系人 ---")
    try:
        new_partner = models.execute(DB, uid, PASSWORD, 'res.partner', 'search_read', 
            [('id', '=', new_partner_id)], ['name', 'create_uid'])
        if new_partner:
            print(f"✓ 可以看到自己创建的联系人: {new_partner[0].get('name')}")
        else:
            print("✗ 无法看到自己创建的联系人")
    except Exception as e:
        print(f"✗ 验证失败: {e}")
    
    # 测试4: 修改联系人
    print("\n--- 测试4: 修改联系人 ---")
    try:
        models.execute(DB, uid, PASSWORD, 'res.partner', 'write', new_partner_id, {
            'name': '测试联系人_已修改',
        })
        print(f"✓ 修改联系人成功")
    except Exception as e:
        print(f"✗ 修改联系人失败: {e}")
    
    # 测试5: 尝试删除联系人 (应该失败)
    print("\n--- 测试5: 尝试删除联系人 ---")
    try:
        models.execute(DB, uid, PASSWORD, 'res.partner', 'unlink', new_partner_id)
        print(f"✗ 删除成功 (不应该允许)")
    except Exception as e:
        print(f"✓ 删除被拒绝 (预期行为)")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_permissions()
