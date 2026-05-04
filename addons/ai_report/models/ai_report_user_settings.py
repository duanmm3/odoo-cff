# -*- coding: utf-8 -*-
from odoo import models, fields


class AiReportUserSettings(models.Model):
    _name = 'ai.report.user.settings'
    _description = 'AI Report 用户设置'

    user_id = fields.Many2one('res.users', '用户', required=True, ondelete='cascade')
    default_chart_type = fields.Selection([
        ('bar', '柱形图'),
        ('line', '折线图'),
        ('pie', '饼图'),
        ('area', '面积图'),
        ('radar', '雷达图'),
        ('scatter', '散点图'),
        ('bar_horizontal', '水平柱形图'),
        ('table', '仅表格'),
    ], '默认图表类型', default='bar')
    enable_auto_recommend = fields.Boolean('启用图表自动推荐', default=True)
    show_table_always = fields.Boolean('始终显示数据表格', default=True)
    chart_color_scheme = fields.Selection([
        ('default', '默认配色'),
        ('warm', '暖色调'),
        ('cool', '冷色调'),
        ('monochrome', '单色'),
    ], '图表配色方案', default='default')
    max_chart_items = fields.Integer('图表最大显示项数', default=20)

    _constraints = [
        ('user_unique', 'unique(user_id)', '每个用户只能有一条设置记录'),
    ]

    @classmethod
    def get_settings(cls):
        """获取当前用户设置"""
        self = cls.env
        settings = cls.search([('user_id', '=', self.env.uid)], limit=1)
        if not settings:
            settings = cls.create({'user_id': self.env.uid})
        return settings