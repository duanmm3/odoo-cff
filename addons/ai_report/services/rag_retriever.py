# -*- coding: utf-8 -*-
"""RAG Retriever — 基于 LanceDB 的 RAG 检索器"""

import logging
from typing import List, Dict

_logger = logging.getLogger(__name__)

try:
    import lancedb
    from sentence_transformers import SentenceTransformer
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    _logger.warning("ai_report: lancedb 或 sentence-transformers 未安装")


class RAGRetriever:
    """基于 LanceDB 的 RAG 检索器"""

    def __init__(self, index_dir: str, mdl_manager):
        self.index_dir = index_dir
        self.mdl_manager = mdl_manager
        self.db = None
        self.encoder = None
        self.table_name = "mdl_embeddings"
        
        if LANCEDB_AVAILABLE:
            try:
                self.db = lancedb.connect(index_dir)
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                _logger.warning(f"ai_report: RAG初始化失败 ({e})")

    def build_index(self):
        """构建/重建向量索引"""
        if not LANCEDB_AVAILABLE or not self.db or not self.encoder:
            _logger.warning("ai_report: RAG组件不可用")
            return
            
        documents = self._extract_documents()
        if not documents:
            return
            
        try:
            embeddings = self.encoder.encode([d['text'] for d in documents])
            data = [
                {
                    'id': d['id'],
                    'text': d['text'],
                    'type': d['type'],
                    'model': d.get('model', ''),
                    'vector': emb.tolist()
                }
                for d, emb in zip(documents, embeddings)
            ]

            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)

            self.db.create_table(self.table_name, data)
        except Exception as e:
            _logger.warning(f"ai_report: 向量索引构建失败 ({e})")

    def _extract_documents(self) -> List[dict]:
        """从 MDL 定义中提取可检索的文档"""
        documents = []

        for name, model in self.mdl_manager.models.items():
            desc = model.get('properties', {}).get('description', '')
            documents.append({
                'id': f"model_{name}",
                'text': f"{name}: {desc}",
                'type': 'model',
                'model': name
            })

            for col in model.get('columns', []):
                col_desc = col.get('description', '')
                if col_desc:
                    documents.append({
                        'id': f"col_{name}_{col['name']}",
                        'text': f"{name}.{col['name']}: {col_desc} ({col['type']})",
                        'type': 'column',
                        'model': name
                    })

        for name, view in self.mdl_manager.views.items():
            desc = view.get('properties', {}).get('description', '')
            documents.append({
                'id': f"view_{name}",
                'text': f"视图 {name}: {desc}",
                'type': 'view',
                'model': ''
            })

        if self.mdl_manager.instructions:
            documents.append({
                'id': "instructions",
                'text': self.mdl_manager.instructions[:500],
                'type': 'instruction',
                'model': ''
            })

        return documents

    def retrieve(self, question: str, top_k: int = 5, role: str = None) -> List[dict]:
        """检索与问题最相关的 Schema 片段"""
        if not self.db or not self.encoder:
            return []
            
        try:
            table = self.db.open_table(self.table_name)
            query_vector = self.encoder.encode([question])[0].tolist()
            results = table.search(query_vector).limit(top_k).to_pandas()
            
            if role and role != 'admin':
                role_models = {
                    'sales': ['sale_order', 'sale_order_line', 'product_product', 'product_template', 'res_partner'],
                    'purchase': ['purchase_order', 'purchase_order_line', 'product_product', 'product_template', 'res_partner'],
                    'warehouse': ['stock_move', 'stock_picking', 'stock_quant', 'product_product', 'product_template'],
                }
                allowed = set(role_models.get(role, []))
                results = results[results['model'].isin(allowed) | (results['model'] == '')]

            return results.to_dict('records')
        except Exception as e:
            _logger.warning(f"ai_report: RAG检索失败 ({e})")
            return []