{
    'name': 'IC Price Query Module',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Electronic component price query system integrated with multiple suppliers',
    'description': """
IC Price Query Module
=====================
This module provides an electronic component price query system that integrates with multiple suppliers:
- Mouser API
- LCSC (crawler)
- Nexar API
- OEMSecrets API
- Qwen AI for supplementary queries

Features:
---------
1. Real-time price query from multiple suppliers
2. Currency conversion to RMB
3. Daily price caching with Redis
4. Historical price tracking
5. CSV export functionality
6. Web interface for easy query
7. API endpoints for integration

Configuration required:
----------------------
1. API keys for Mouser, Nexar, OEMSecrets, Qwen
2. Redis server connection
3. Exchange rate API access
""",
    'author': 'Odoo Price Module',
    'website': '',
    'depends': ['base', 'web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/price_query_views.xml',
        'views/price_menu_views.xml',
        'views/price_query_page.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [
            'redis',
            'requests',
            'flask',
            'openai',
            'playwright',
            'beautifulsoup4',
        ],
    },
}