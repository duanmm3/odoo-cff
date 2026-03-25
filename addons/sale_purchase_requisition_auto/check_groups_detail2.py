#!/usr/bin/env python3
import xmlrpc.client

url = 'http://localhost:8070'
db = 'app'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("检查用户组...")
# Alan
alan_user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [21, ['name', 'group_ids']])
print(f"Alan: {alan_user}")

# Susan  
susan_user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [39, ['name', 'group_ids']])
print(f"Susan: {susan_user}")

# 检查组的完整信息
print("\n检查组75,76,77...")
for gid in [75, 76, 77]:
    g = models.execute_kw(db, uid, 'admin', 'res.groups', 'read', [gid, ['name', 'users']])
    print(f"  {gid}: {g[0]}")

# 检查记录规则 - 我们的自定义规则
print("\n检查自定义记录规则...")
custom_rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'search', [[('name', 'ilike', '销售组'), ('name', 'ilike', '采购')]])
print(f"销售组采购规则: {custom_rules}")

custom_rules = models.execute_kw(db, uid, 'admin', 'ir.rule', 'search', [[('name', 'ilike', '采购组'), ('name', 'ilike', '销售')]])
print(f"采购组销售规则: {custom_rules}")