# sale_purchase_requisition_auto 模块说明

## 概述

本模块实现销售与采购的协同工作流程，并提供基于用户组的权限控制功能。

## 主要功能

### 1. 自动采购需求创建
当销售订单中的产品库存不足时，系统会自动创建采购需求单（Purchase Requisition），并通知采购负责人处理。

### 2. 用户组权限控制
模块定义了三个用户组来实现精细化的权限控制：

| 组名称 | 说明 |
|--------|------|
| 销售组 (Sales Team) | 销售用户，只能看自己的销售订单和采购订单 |
| 采购组 (Purchase Team) | 采购用户，只能看自己的采购订单和销售订单 |
| 管理员组 (Admin Team) | 管理员，可查看所有数据 |

### 3. 记录规则（Record Rules）

通过ir.rule实现数据隔离：

- **销售组采购订单规则**：销售用户只能看到自己创建的采购订单
- **采购组销售订单规则**：采购用户只能看到自己创建的销售订单

## 文件结构

```
sale_purchase_requisition_auto/
├── __init__.py                 # 模块初始化文件
├── __manifest__.py             # 模块清单文件
├── models/
│   ├── __init__.py             # 模型初始化
│   ├── product_template.py     # 产品模板扩展
│   ├── sale_order.py           # 销售订单扩展
│   └── wizard.py               # 向导（库存不足时弹出）
├── views/
│   ├── product_template_views.xml
│   ├── sale_order_views.xml
│   └── wizard_views.xml
└── security/
    ├── groups.xml              # 用户组和记录规则定义
    ├── acl.csv                # 访问控制列表
    └── ir.model.access.csv    # 模型访问权限
```

## 用户组与成员

### 销售组 (ID: 76)
- Alan, Amanda, Cathy, Emma, Ferpa, Milne, Suwen, Vivian
- 权限：可访问销售订单、库存、发票；只能看到自己创建的采购订单

### 采购组 (ID: 75)
- Spring, Crystal, Susan, Sunny
- 权限：可访问采购订单、库存；只能看到自己创建的销售订单

### 管理员组 (ID: 77)
- Coco, cc
- 权限：可访问所有数据

## 业务流程

1. **销售创建订单** → 销售创建销售订单（如产品cff3，数量110）
2. **库存检查** → 系统检查库存是否充足
3. **缺货处理** → 如果库存不足，弹出向导让用户选择采购数量
4. **创建采购需求** → 自动创建采购需求单，分配给指定采购员
5. **采购处理** → 采购员收到需求，管理员审批后进行采购
6. **入库** → 产品入库，更新库存
7. **开票** → 销售创建发票，完成出库

## 权限验证结果

| 用户 | 角色 | 采购订单 | 销售订单 | 库存 |
|------|------|----------|----------|------|
| Alan | 销售组 | 0 | 7 | 可见 |
| Susan | 采购组 | 23 | 0 | 可见 |
| Admin | 管理员 | 23 | 35 | 可见 |

## 升级模块

在Odoo后台：应用 → 找到"sale_purchase_requisition_auto" → 点击"升级"

## 技术细节

### XML-RPC接口
模块使用XML-RPC与Odoo服务器通信：
- URL: http://localhost:8070
- 数据库: app
- 管理员: admin / admin

### 主要模型
- `sale.order`: 销售订单
- `purchase.order`: 采购订单
- `purchase.requisition`: 采购需求
- `stock.quant`: 库存
- `account.move`: 发票

## 开发者说明

### 添加新用户到组
可通过Odoo后台：设置 → 用户 → 编辑用户 → 访问权限

或使用XML-RPC编程方式添加。

### 修改记录规则
记录规则定义在 `security/groups.xml` 文件中，修改后需要升级模块才能生效。