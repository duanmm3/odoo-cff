# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
产品模板扩展模块

本模块为产品模板添加了采购负责人字段，用于指定负责采购该产品的人员。
当库存不足时，系统会通知该负责人处理采购需求。
"""

from odoo import fields, models


class ProductTemplate(models.Model):
    """
    继承自product.template，扩展产品模板的字段
    
    新增字段：
    - purchase_responsible_id: 采购负责人
    """
    _inherit = 'product.template'

    # 采购负责人字段：指定谁负责采购该产品
    # 当库存不足创建采购需求时，系统会通知此人员
    purchase_responsible_id = fields.Many2one(
        'res.users',
        string='采购负责人',  # 字段显示名称（中文）
        tracking=True,        # 启用跟踪，当字段值变化时会记录到消息中
        check_company=True,   # 启用公司检查，确保只能选择当前公司的用户
        help='负责此产品采购的人员，库存不足时将收到通知'
    )
