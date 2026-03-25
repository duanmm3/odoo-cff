# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Auto Purchase Requisition',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Auto create purchase requisition when sales order has insufficient stock',
    'description': """
Sale Order Auto Purchase Requisition
====================================
当销售订单库存不足时，自动创建采购需求单并通知采购负责人。

功能：
- 销售订单创建时检查库存
- 库存不足时弹出向导让用户选择采购数量
- 自动创建采购需求单（Purchase Requisition）
- 通知采购负责人处理
    """,
    'author': 'CFF',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'purchase',
        'purchase_requisition',
        'stock',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/acl.csv',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
