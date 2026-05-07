{
    'name': ' Custom Price Module',
    'version': '2.0',
    'category': 'Sales',
    'summary': 'Inquiry analysis system for sales and purchase collaboration',
    'description': """
Inquiry Analysis Module
=======================
This module provides a complete inquiry analysis solution for Odoo 19 Community Edition,
enabling seamless collaboration between sales and purchase teams.

Features:
---------
1. Inquiry request management - Sales create and manage inquiry requests
2. Purchase quotation - Purchase team provides quotes for requests
3. Price comparison analysis - Automatic calculation of best prices
4. Sales order generation - Confirm requests and generate sales orders
5. Permission isolation - Purchase can only see their own quotes
6. Bulk import functionality - Support for batch inquiry creation

Business Process:
----------------
Sales Create Request → Purchase Quote → Price Analysis → Confirm → Sales Order
""",
    'author': 'Odoo Inquiry Analysis Team',
    'website': '',
    'depends': ['base', 'sale', 'purchase', 'product', 'sales_team'],
    'data': [
        'security/inquiry_security.xml',
        'security/ir.model.access.csv',
        'data/inquiry_sequence.xml',
        'views/inquiry_request_views.xml',
        'views/inquiry_quote_views.xml',
        'views/inquiry_menu_views.xml',
        'views/inquiry_import_wizard_views.xml',
        'views/inquiry_request_page.xml',
        'views/price_query_page.xml',
        'views/price_query_views.xml',
        'views/price_menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'license': 'LGPL-3',
}