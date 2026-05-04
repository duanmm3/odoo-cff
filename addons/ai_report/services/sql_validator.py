# -*- coding: utf-8 -*-
"""SQL Validator — SQL 安全校验器"""

import re


class SQLValidator:
    """SQL 安全校验器"""

    FORBIDDEN_KEYWORDS = ['DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE', 'COPY']
    FORBIDDEN_FUNCTIONS = ['pg_sleep', 'pg_terminate_backend', 'pg_cancel_backend', 'lo_import', 'lo_export', 'pg_read_file', 'pg_write_file']
    MAX_EXECUTION_TIME = 30
    MAX_RETURN_ROWS = 1000

    @classmethod
    def validate(cls, sql: str, role: str = None, allowed_tables: list = None) -> dict:
        """校验 SQL 安全性"""
        sql_upper = sql.upper().strip()

        for kw in cls.FORBIDDEN_KEYWORDS:
            pattern = r'\b' + kw + r'\b'
            if re.search(pattern, sql_upper):
                return {'valid': False, 'error': f'SQL 包含禁止的操作: {kw}'}

        for func in cls.FORBIDDEN_FUNCTIONS:
            if func in sql_upper:
                return {'valid': False, 'error': f'SQL 包含禁止的函数: {func}'}

        if not sql_upper.startswith('SELECT'):
            return {'valid': False, 'error': '仅允许 SELECT 查询'}

        if 'LIMIT' not in sql_upper:
            sql = sql.rstrip(';') + f' LIMIT {cls.MAX_RETURN_ROWS}'

        return {'valid': True, 'error': None, 'safe_sql': sql}