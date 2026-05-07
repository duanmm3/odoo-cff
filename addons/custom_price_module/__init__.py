from . import models
from . import controllers

from odoo import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)
_logger.info("inquiry_analysis module loaded")


def _cleanup_invalid_user_domain_records(env):
    for model_name, field_name in [
        ('ir.rule', 'domain_force'),
        ('ir.filters', 'domain'),
        ('ir.actions.act_window', 'domain'),
    ]:
        records = env[model_name].search([(field_name, 'ilike', 'user.id')])
        for record in records:
            old_domain = getattr(record, field_name) or ''
            new_domain = old_domain.replace('user.id', 'uid')
            if new_domain != old_domain:
                _logger.info(
                    'Fixing invalid domain on %s %s: %s -> %s',
                    model_name, record.name or record.id, old_domain, new_domain
                )
                record.write({field_name: new_domain})


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _cleanup_invalid_user_domain_records(env)
    purchase_group = env.ref('purchase.group_purchase_user', raise_if_not_found=False)
    if not purchase_group:
        return
    purchase_logins = ['Cathy', 'Susan', 'Spring', 'Crystal', 'Sunny']
    users = env['res.users'].search([('login', 'in', purchase_logins), ('active', '=', True)])
    if not users:
        users = env['res.users'].search([('name', 'in', purchase_logins), ('active', '=', True)])
    if users:
        purchase_group.users = [(4, user.id) for user in users]