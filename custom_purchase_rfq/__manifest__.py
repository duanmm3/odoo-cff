# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase RFQ Price Control',
    'version': '1.0',
    'category': 'Purchase',
    'summary': '控制采购用户修改销售创建的RFQ价格',
    'description': """
        限制采购用户修改销售创建的RFQ价格
        ================================
        
        功能:
        - 销售创建的RFQ，价格字段对采购用户只读
        - 采购只能确认或拒绝RFQ，不能修改价格
        - 销售可以修改自己创建的RFQ价格
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['purchase', 'sale'],
    'data': [
        'security/ir_rule.xml',
        'views/purchase_order_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
