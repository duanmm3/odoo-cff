# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""ai_report - Chat2BI Module for Odoo 19

基于WrenAI语义层嵌入的Chat2BI模块，实现自然语言查询和数据可视化。
"""

from . import models
from . import services
from . import controllers

from .hooks import post_init_hook, uninstall_hook