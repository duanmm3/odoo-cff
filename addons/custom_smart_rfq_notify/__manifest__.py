# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Smart RFQ Notification',
    'version': '1.0',
    'category': 'Purchase',
    'summary': '智能RFQ竞价通知系统',
    'description': """
        智能RFQ竞价通知系统
        ==================
        
        功能:
        - 基于历史报价数据，智能选择优先供应商
        - 24小时超时自动通知更多供应商竞价
        - 记录供应商报价历史
        - 报价对比界面
        
        工作流程:
        1. 销售创建RFQ
        2. 系统自动选择有历史报价的供应商优先通知
        3. 等待24小时
        4. 如无报价，自动通知所有供应商竞价
        5. 采购报价后，销售可比较选择最优价格
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['purchase', 'sale'],
    'data': [
        'security/ir_model_access.csv',
        'views/purchase_order_views.xml',
        'views/purchase_vendor_quote_history_views.xml',
        'data/cron_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
