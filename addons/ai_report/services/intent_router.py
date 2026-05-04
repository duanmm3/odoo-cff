# -*- coding: utf-8 -*-
"""Intent Router — 意图识别与路由"""

import logging
from typing import Dict

_logger = logging.getLogger(__name__)


class IntentRouter:
    """意图识别与路由"""

    INTENT_MAP = {
        'query': {'handler': 'chat2bi', 'method': 'process_query'},
        'sale_create': {'handler': 'dml', 'method': 'create_sale_order'},
        'sale_update': {'handler': 'dml', 'method': 'update_sale_order'},
        'sale_delete': {'handler': 'dml', 'method': 'delete_sale_order'},
        'purchase_create': {'handler': 'dml', 'method': 'create_purchase_order'},
        'purchase_update': {'handler': 'dml', 'method': 'update_purchase_order'},
        'purchase_delete': {'handler': 'dml', 'method': 'delete_purchase_order'},
        'stock_in': {'handler': 'dml', 'method': 'stock_in'},
        'stock_out': {'handler': 'dml', 'method': 'stock_out'},
    }

    KEYWORD_MAP = {
        'sale_create': ['创建销售', '新建销售', '新增销售', '下销售单', '建销售订单'],
        'sale_update': ['修改销售', '更新销售', '变更销售', '改销售订单'],
        'sale_delete': ['删除销售', '取消销售', '作废销售'],
        'purchase_create': ['创建采购', '新建采购', '新增采购', '下采购单'],
        'purchase_update': ['修改采购', '更新采购', '变更采购'],
        'purchase_delete': ['删除采购', '取消采购', '作废采购'],
        'stock_in': ['入库', '收货', '进货', '验收'],
        'stock_out': ['出库', '发货', '出货', '配送'],
        'query': ['查', '看', '统计', '分析', '多少', '哪些', '排行', '趋势', '畅销', '销售'],
    }

    def route(self, question: str) -> Dict:
        """路由用户问题到对应的处理器"""
        for intent, keywords in self.KEYWORD_MAP.items():
            for kw in keywords:
                if kw in question:
                    return {
                        'intent': intent,
                        'confidence': 0.8,
                        'method': 'keyword'
                    }
        return {'intent': 'query', 'confidence': 0.5, 'method': 'default'}