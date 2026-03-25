# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Business Approval Flow',
    'version': '1.0',
    'category': 'Generic',
    'summary': '业务审批流程系统',
    'description': """
        业务审批流程系统
        ===============
        
        功能:
        - 销售订单需要销售经理审批
        - 采购订单需要采购经理审批
        - 采购修改销售订单价格需要审批
        - 发票支付需要财务经理审批
        
        审批流程:
        1. 申请人提交审批请求
        2. 审批人收到站内通知
        3. 审批人审核通过/拒绝
        4. 自动更新原单据状态
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'purchase', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/sale_order_approval.xml',
        # 'views/purchase_order_approval.xml',  # 暂时注释，先让模块安装成功
        'views/account_move_approval.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
