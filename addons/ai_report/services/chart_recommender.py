# -*- coding: utf-8 -*-
"""Chart Recommender — 图表自动推荐引擎"""

from typing import List, Dict


class ChartRecommender:
    """图表自动推荐引擎"""

    @classmethod
    def recommend(cls, columns: list, data: list, query_type: str = None) -> List[Dict]:
        """根据数据特征推荐图表类型"""
        if not data:
            return [{'type': 'table', 'reason': '无数据', 'priority': 1}]

        recommendations = []
        numeric_cols = cls._find_numeric_columns(columns, data)
        category_cols = cls._find_category_columns(columns, data)
        date_cols = cls._find_date_columns(columns, data)
        row_count = len(data)

        if date_cols and numeric_cols:
            recommendations.append({'type': 'line', 'reason': '数据包含时间维度，适合展示趋势', 'priority': 1})
            recommendations.append({'type': 'area', 'reason': '面积图展示累计趋势', 'priority': 2})

        if category_cols and numeric_cols and row_count <= 8:
            recommendations.append({'type': 'pie', 'reason': f'数据共{row_count}行，适合展示占比', 'priority': 1})

        if category_cols and numeric_cols:
            recommendations.append({'type': 'bar', 'reason': '分类数据适合柱形图对比', 'priority': 1})

        if len(numeric_cols) >= 3 and row_count <= 8:
            recommendations.append({'type': 'radar', 'reason': '多维度数据适合雷达图对比', 'priority': 2})

        if len(numeric_cols) >= 2:
            recommendations.append({'type': 'scatter', 'reason': '多数值维度可展示相关性', 'priority': 3})

        recommendations.append({'type': 'table', 'reason': '数据表格展示精确数值', 'priority': 10})
        recommendations.sort(key=lambda x: x['priority'])
        return recommendations

    @classmethod
    def _find_numeric_columns(cls, columns, data):
        """识别数值列"""
        numeric = []
        for i, col in enumerate(columns):
            if data and isinstance(data[0][i], (int, float)):
                numeric.append(col)
        return numeric

    @classmethod
    def _find_category_columns(cls, columns, data):
        """识别分类列"""
        categories = []
        for i, col in enumerate(columns):
            if data and isinstance(data[0][i], str):
                categories.append(col)
        return categories

    @classmethod
    def _find_date_columns(cls, columns, data):
        """识别日期列"""
        date_keywords = ['date', 'month', 'year', 'week', 'time', '日期', '月份', '年份']
        return [c for c in columns if any(kw in c.lower() for kw in date_keywords)]