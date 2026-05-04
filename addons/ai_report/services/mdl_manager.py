# -*- coding: utf-8 -*-
"""MDL Manager — Wren Engine 的 Python 轻量替代"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional


class MDLManager:
    """管理 Wren MDL 语义层定义"""

    def __init__(self, mdl_base_path: str):
        self.mdl_base_path = Path(mdl_base_path)
        self.models: Dict[str, dict] = {}
        self.relationships: List[dict] = []
        self.views: Dict[str, dict] = {}
        self.instructions: str = ""
        self._load_all()

    def _load_all(self):
        """加载所有 MDL 定义文件"""
        self._load_project_config()
        self._load_models()
        self._load_relationships()
        self._load_views()
        self._load_instructions()

    def _load_project_config(self):
        """加载项目配置"""
        config_path = self.mdl_base_path / "wren_project.yml"
        if config_path.exists():
            with open(config_path, encoding='utf-8') as f:
                self.project_config = yaml.safe_load(f) or {}

    def _load_models(self):
        """加载所有模型定义"""
        models_dir = self.mdl_base_path / "models"
        if not models_dir.exists():
            return
        for model_dir in models_dir.iterdir():
            if model_dir.is_dir():
                metadata_path = model_dir / "metadata.yml"
                if metadata_path.exists():
                    with open(metadata_path, encoding='utf-8') as f:
                        model_def = yaml.safe_load(f) or {}
                    ref_sql_path = model_dir / "ref_sql.sql"
                    if ref_sql_path.exists():
                        model_def['ref_sql'] = ref_sql_path.read_text(encoding='utf-8')
                    self.models[model_def.get('name', model_dir.name)] = model_def

    def _load_relationships(self):
        """加载关系定义"""
        rel_path = self.mdl_base_path / "relationships.yml"
        if rel_path.exists():
            with open(rel_path, encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            self.relationships = data.get('relationships', [])

    def _load_views(self):
        """加载视图定义"""
        views_dir = self.mdl_base_path / "views"
        if not views_dir.exists():
            return
        for view_dir in views_dir.iterdir():
            if view_dir.is_dir():
                metadata_path = view_dir / "metadata.yml"
                if metadata_path.exists():
                    with open(metadata_path, encoding='utf-8') as f:
                        view_def = yaml.safe_load(f) or {}
                    self.views[view_def.get('name', view_dir.name)] = view_def

    def _load_instructions(self):
        """加载业务指令"""
        inst_path = self.mdl_base_path / "instructions.md"
        if inst_path.exists():
            self.instructions = inst_path.read_text(encoding='utf-8')

    def get_schema_context(self, role: str = None) -> str:
        """根据角色获取 Schema 上下文"""
        role_model_map = {
            'sales': ['sale_order', 'sale_order_line', 'product_product', 'product_template', 'res_partner'],
            'purchase': ['purchase_order', 'purchase_order_line', 'product_product', 'product_template', 'res_partner'],
            'warehouse': ['stock_move', 'stock_picking', 'stock_quant', 'product_product', 'product_template'],
            'admin': list(self.models.keys()),
        }
        allowed_models = role_model_map.get(role, role_model_map.get('admin', []))
        context_parts = []

        for model_name in allowed_models:
            if model_name in self.models:
                model = self.models[model_name]
                context_parts.append(self._model_to_prompt(model))

        relevant_rels = [r for r in self.relationships if any(m in allowed_models for m in r.get('models', []))]
        if relevant_rels:
            context_parts.append("\n## 表关系")
            for rel in relevant_rels:
                context_parts.append(f"- {rel.get('models', [''])[0]} <-> {rel.get('models', [''])[1]}: {rel.get('condition', '')} ({rel.get('join_type', '')})")

        if self.instructions:
            context_parts.append(f"\n## 业务规则\n{self.instructions}")

        return "\n".join(context_parts)

    def _model_to_prompt(self, model: dict) -> str:
        """将模型定义转换为 LLM 可理解的文本"""
        lines = [f"\n### {model.get('name', '')}"]
        props = model.get('properties', {})
        if props.get('description'):
            lines.append(f"描述: {props['description']}")
        lines.append("字段:")
        for col in model.get('columns', []):
            desc = col.get('description', '')
            calc = " (计算字段)" if col.get('is_calculated') else ""
            pk = " [主键]" if col.get('is_primary_key') else ""
            lines.append(f"  - {col['name']} ({col['type']}){calc}{pk}: {desc}")
        return "\n".join(lines)

    def validate_sql(self, sql: str, role: str = None) -> dict:
        """校验生成的 SQL 是否合法"""
        forbidden = ['DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE', 'INSERT', 'UPDATE', 'DELETE']
        sql_upper = sql.upper().strip()
        
        for kw in forbidden:
            if kw in sql_upper:
                return {'valid': False, 'error': f'SQL 包含禁止的关键字: {kw}'}

        if role:
            role_model_map = {
                'sales': ['sale_order', 'sale_order_line', 'product_product', 'product_template', 'res_partner'],
                'purchase': ['purchase_order', 'purchase_order_line', 'product_product', 'product_template', 'res_partner'],
                'warehouse': ['stock_move', 'stock_picking', 'stock_quant', 'product_product', 'product_template'],
                'admin': list(self.models.keys()),
            }
            allowed_tables = set(role_model_map.get(role, []))
            for model_name, model_def in self.models.items():
                table_ref = model_def.get('table_reference', {})
                table_name = table_ref.get('table', model_name)
                if table_name.upper() in sql_upper:
                    if model_name not in allowed_tables:
                        return {'valid': False, 'error': f'角色 {role} 无权访问表 {table_name}'}

        return {'valid': True, 'error': None, 'tables': []}