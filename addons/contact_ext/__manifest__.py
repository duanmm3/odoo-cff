{
    'name': 'Custom Customer Extend',
    'version': '1.7',
    'summary': 'Extended partner information with customer/supplier classification',
    'description': """
        This module extends the partner (contact) model to include:
        1. Customer/Supplier classification
        2. Customer types (CF, CT, OF, OT)
        3. Supplier types (ST, SF, SD, SE)
        4. Automatic code generation
        5. Additional business fields
        6. File upload functionality for documents
        7. Permission control: users can only see their own or shared contacts
    """,
    'category': 'Customer Relationship Management',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/access_control.xml',
        'security/res_partner_security.xml',
        'views/res_partner_views.xml',
        'data/contacts_action.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
