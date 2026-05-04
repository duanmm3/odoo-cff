# -*- coding: utf-8 -*-
"""Query Cache — 查询缓存服务"""

import hashlib
import json
import logging
from odoo import api, models, fields
from datetime import timedelta

_logger = logging.getLogger(__name__)


class QueryCacheService(models.AbstractModel):
    _name = 'ai.report.query.cache.service'
    _description = '查询缓存服务'

    @api.model
    def get_cached(self, question: str, role: str, ttl: int = 3600):
        """获取缓存结果"""
        try:
            cache_model = self.env['ai.report.query.cache']
            return cache_model.get_cached(question, role, ttl)
        except:
            return None

    @api.model
    def set_cache(self, question: str, role: str, result: dict, ttl: int = 3600):
        """设置缓存"""
        try:
            cache_model = self.env['ai.report.query.cache']
            cache_model.set_cache(question, role, result, ttl)
        except Exception as e:
            _logger.warning(f"ai_report: 缓存设置失败 ({e})")