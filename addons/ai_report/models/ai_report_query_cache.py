# -*- coding: utf-8 -*-
from odoo import models, fields, api
import hashlib
import json
from datetime import timedelta


class AiReportQueryCache(models.Model):
    _name = 'ai.report.query.cache'
    _description = 'AI Report 查询缓存'
    _order = 'create_date desc'

    question_hash = fields.Char('问题哈希', index=True)
    question = fields.Text('原始问题')
    role = fields.Char('用户角色')
    sql = fields.Text('生成的 SQL')
    result_json = fields.Text('结果 JSON')
    hit_count = fields.Integer('命中次数', default=0)
    create_date = fields.Datetime('创建时间')
    expire_date = fields.Datetime('过期时间')

    @api.model
    def get_cached(self, question, role, ttl=3600):
        """获取缓存结果"""
        q_hash = hashlib.md5(f"{question}_{role}".encode()).hexdigest()
        cache = self.search([
            ('question_hash', '=', q_hash),
            ('expire_date', '>', fields.Datetime.now()),
        ], limit=1)
        if cache:
            cache.hit_count += 1
            return json.loads(cache.result_json)
        return None

    @api.model
    def set_cache(self, question, role, result, ttl=3600):
        """设置缓存"""
        q_hash = hashlib.md5(f"{question}_{role}".encode()).hexdigest()
        expire = fields.Datetime.now() + timedelta(seconds=ttl)
        self.create({
            'question_hash': q_hash,
            'question': question,
            'role': role,
            'sql': result.get('sql', ''),
            'result_json': json.dumps(result, ensure_ascii=False),
            'expire_date': expire,
        })