#!/usr/bin/env python3
"""
检查并清除 Odoo 缓存
"""

import xmlrpc.client

URL = 'http://129.150.51.7:8069'
common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

uid = common.authenticate('app', 'admin', 'admin', {})

# 清除 assets 缓存
print("=== 清除缓存 ===")

try:
    # 清除 QWeb 缓存
    models.execute('app', uid, 'admin', 'ir.qweb', 'clear_caches', [])
    print("✓ QWeb 缓存已清除")
except Exception as e:
    print(f"✗ {e}")

try:
    # 清除视图缓存
    models.execute('app', uid, 'admin', 'ir.ui.view', 'invalidate_cache', [])
    print("✓ 视图缓存已清除")
except:
    pass

print("\n完成! 请刷新浏览器页面测试")
