# -*- coding: utf-8 -*-
"""Chat2BI Service — NL2SQL 核心引擎"""

import json
import logging
import os
import time
from odoo import api, models

_logger = logging.getLogger(__name__)


class Chat2BIService(models.AbstractModel):
    _name = 'ai.report.chat2bi'
    _description = 'Chat2BI NL2SQL Engine'

    NL2SQL_SYSTEM_PROMPT = """你是 Odoo ERP 的智能 SQL 生成助手。根据用户的自然语言问题和提供的数据库 Schema 信息，生成准确的 PostgreSQL 查询 SQL。

## 重要规则
1. 销售订单的金额必须从 sale_order_line 表计算：SUM(price_unit * product_uom_qty)
2. 不要使用 sale_order.amount_total，那是含税总额，不准确
3. 销售订单状态: state = 'sale' 或 'done' 表示已确认
4. 采购订单状态: state = 'purchase' 或 'done' 表示已确认
5. 日期过滤用: date_order >= DATE_TRUNC('month', CURRENT_DATE) AND date_order < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
6. **销售/采购/库存等统计必须按月份分组！使用 TO_CHAR(date_order, 'YYYY-MM') AS month**
7. 指标字段必须使用 "index" 作为别名，例如：SUM(...) AS index
8. 产品统计时按产品名称分组，不要按月份分组
9. 产品统计使用：JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id，然后使用 pt.name AS product_name

## 数据库 Schema
{schema_context}

## 业务规则
- "最近" 默认指最近 30 天
- "本月" 指当前自然月
- "今年" 指当前自然年
- 金额字段使用 ROUND(CAST(SUM(...) AS NUMERIC), 2) 保留 2 位小数

## 输出格式
返回 JSON 格式：
{{"sql": "生成的SQL", "explanation": "查询说明", "chart_suggestion": "推荐的图表类型"}}

## 重要约束
1. 仅生成 SELECT 查询，禁止任何 DML 操作
2. 指标字段必须使用 AS index 别名
3. 销售/采购/库存查询必须按 month 分组
4. 产品相关查询（排名、汇总等）必须使用 COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) AS product_name
5. 今年销售示例：SELECT TO_CHAR(so.date_order, 'YYYY-MM') AS month, SUM(sol.price_unit * sol.product_uom_qty) AS index FROM sale_order so JOIN sale_order_line sol ON so.id = sol.order_id WHERE so.state IN ('sale', 'done') AND EXTRACT(YEAR FROM so.date_order) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY TO_CHAR(so.date_order, 'YYYY-MM') ORDER BY month
6. 产品排名示例：SELECT COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) AS product_name, SUM(sol.product_uom_qty) AS index FROM sale_order_line sol JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN sale_order so ON sol.order_id = so.id WHERE so.state IN ('sale', 'done') GROUP BY COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) ORDER BY index DESC LIMIT 10
7. 库存预警示例：SELECT COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) AS product_name, sum(sq.quantity) AS index FROM stock_quant sq JOIN product_product pp ON sq.product_id = pp.id LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id WHERE sq.quantity < 10 group by COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) ORDER BY index ASC
8. 产品销售汇总示例：SELECT COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) AS product_name, SUM(sol.product_uom_qty) AS qty, SUM(sol.price_unit * sol.product_uom_qty) AS amount FROM sale_order_line sol JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN sale_order so ON sol.order_id = so.id WHERE so.state IN ('sale', 'done') GROUP BY COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US'))
9. 年度采购分析示例：SELECT TO_CHAR(po.date_order, 'YYYY-MM') AS month, SUM(pol.price_unit * pol.product_qty) AS index FROM purchase_order po JOIN purchase_order_line pol ON po.id = pol.order_id WHERE po.state IN ('purchase', 'done') AND EXTRACT(YEAR FROM po.date_order) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY TO_CHAR(po.date_order, 'YYYY-MM') ORDER BY month
10. 采购产品排行示例：SELECT COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) AS product_name, SUM(pol.product_qty) AS index FROM purchase_order_line pol JOIN product_product pp ON pol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id JOIN purchase_order po ON pol.order_id = po.id WHERE po.state IN ('purchase', 'done') GROUP BY COALESCE(pp.default_code, COALESCE(pt.name->>'zh_CN', pt.name->>'en_US')) ORDER BY index DESC LIMIT 10
11. 采购趋势分析示例：SELECT TO_CHAR(po.date_order, 'YYYY-MM') AS month, SUM(pol.price_unit * pol.product_qty) AS index FROM purchase_order po JOIN purchase_order_line pol ON po.id = pol.order_id WHERE po.state IN ('purchase', 'done') AND po.date_order >= CURRENT_DATE - INTERVAL '12 months' GROUP BY TO_CHAR(po.date_order, 'YYYY-MM') ORDER BY month
"""

    @api.model
    def process_query(self, question: str, session_id: str = None) -> dict:
        """处理自然语言查询的完整流程"""
        start_time = time.time()
        
        role = self._get_user_role()
        _logger.info(f"Chat2BI: 用户角色={role}, 问题={question} session={session_id}")

        permission = self.env['ai.report.permission'].check_query_permission(role, question)
        if not permission['allowed']:
            return {'type': 'error', 'message': permission['reason']}

        schema_context = self._build_schema_context(role)
        prompt = self._build_nl2sql_prompt(question, schema_context, session_id)

        try:
            llm_result = self._call_llm_for_sql(prompt)
        except Exception as e:
            return {'type': 'error', 'message': f'LLM调用失败: {str(e)}'}

        chart_suggestion = self._normalize_chart_type(llm_result.get('chart_suggestion', 'bar'))

        try:
            columns, data = self._execute_sql(llm_result.get('sql', ''))
        except Exception as e:
            return {'type': 'error', 'message': f"SQL 执行失败: {str(e)}", 'sql': llm_result.get('sql', ''), 'chart_suggestion': chart_suggestion}

        execution_time = time.time() - start_time
        return {
            'type': 'query',
            'sql': llm_result.get('sql', ''),
            'explanation': llm_result.get('explanation', ''),
            'chart_suggestion': chart_suggestion,
            'columns': columns,
            'data': data,
            'row_count': len(data),
            'execution_time': execution_time,
        }

    def _get_user_role(self) -> str:
        """获取当前用户角色"""
        return self.env['ai.report.permission'].get_user_role()

    def _build_schema_context(self, role: str) -> str:
        """构建 Schema 上下文"""
        try:
            mdl_path = os.path.join(os.path.dirname(__file__), 'models', 'mdl')
            from .mdl_manager import MDLManager
            mdl_manager = MDLManager(mdl_path)
            return mdl_manager.get_schema_context(role)
        except Exception as e:
            _logger.warning(f"ai_report: MDL加载失败 ({e})")
            return self._get_basic_schema()

    def _get_basic_schema(self) -> str:
        """获取基础 Schema"""
        return """
### sale_order (销售订单)
- id: 主键
- name: 订单编号
- partner_id: 客户ID (外键到 res.partner)
- date_order: 订单日期
- state: 状态(draft/sale/done/cancel)
- amount_total: 订单总额 (含税)
- user_id: 销售员ID (外键到 res.users)

### sale_order_line (销售订单行)
- id: 主键
- order_id: 订单ID (外键到 sale_order)
- product_id: 产品ID (外键到 product.product)
- name: 产品描述
- product_uom_qty: 数量
- price_unit: 单价
- price_subtotal: 小计
- state: 行状态

### purchase_order (采购订单)
- id: 主键
- name: 订单编号
- partner_id: 供应商ID (外键到 res.partner)
- date_order: 订单日期
- state: 状态
- amount_total: 订单总额

### purchase_order_line (采购订单行)
- id: 主键
- order_id: 订单ID (外键到 purchase_order)
- product_id: 产品ID
- product_qty: 数量
- price_unit: 单价

### product_product (产品)
- id: 主键
- name: 产品名称
- default_code: SKU
- product_tmpl_id: 产品模板ID

### product_template (产品模板)
- id: 主键
- name: 产品名称
- type: 类型(product/service)

### stock_move (库存移动)
- id: 主键
- product_id: 产品ID
- product_uom_qty: 数量
- state: 状态(draft/done/cancel)
- date: 日期
- location_id: 源位置ID
- location_dest_id: 目标位置ID

重要：销售额必须用 sale_order_line 的 price_unit * product_uom_qty 计算，不能用 sale_order 的 amount_total！
"""

    def _normalize_chart_type(self, chart_type: str) -> str:
        if not chart_type:
            return 'bar'
        key = chart_type.strip().lower()
        if key in ['bar', 'column', '柱状', '柱形', '柱状图', '柱形图']:
            return 'bar'
        if key in ['line', '折线', '折线图']:
            return 'line'
        if key in ['pie', '饼', '饼图']:
            return 'pie'
        if key in ['radar', '雷达', '雷达图']:
            return 'radar'
        return 'bar'

    def _get_conversation_context(self, session_id: str) -> str:
        if not session_id:
            return ''
        try:
            chats = self.env['ai.report.chat'].search([('session_id', '=', session_id)], order='create_date asc')
            context_lines = []
            for chat in chats:
                if chat.message_type == 'user':
                    context_lines.append(f"用户: {chat.content}")
                else:
                    context_lines.append(f"助手: {chat.content}")
            return '\n'.join(context_lines)
        except Exception:
            return ''

    def _build_nl2sql_prompt(self, question: str, schema_context: str, session_id: str = None) -> list:
        """构建 NL2SQL Prompt"""
        system_prompt = self.NL2SQL_SYSTEM_PROMPT.format(schema_context=schema_context)
        conversation_context = self._get_conversation_context(session_id)
        user_prompt = f"""根据以下问题生成 SQL 查询：

问题：{question}

注意：
- 销售数据从 sale_order_line 表计算金额
- 使用正确的 JOIN 连接表
- 返回 JSON 格式：{{"sql": "SELECT ...", "explanation": "查询说明", "chart_suggestion": "bar/pie/line/table"}}
"""
        if conversation_context:
            user_prompt = f"历史对话：\n{conversation_context}\n\n" + user_prompt
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _call_llm_for_sql(self, prompt: list) -> dict:
        """调用 LLM 生成 SQL"""
        import requests
        
        api_base = self.env['ir.config_parameter'].sudo().get_param('ai_report.llm_api_base', '')
        
        # 清理 URL 末尾的斜杠
        api_base = api_base.rstrip('/')
        
        _logger.info(f"LLM API URL: {api_base}/v1/chat/completions")
        
        try:
            response = requests.post(
                f"{api_base}/v1/chat/completions",
                json={
                    "model": "any-model",
                    "messages": prompt,
                    "temperature": 0,
                    "max_tokens": 4096,
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                return json.loads(content)
            except:
                return {"sql": content, "explanation": "", "chart_suggestion": "table"}
        except Exception as e:
            _logger.error(f"ai_report: LLM调用失败 ({e})")
            raise

    def _execute_sql(self, sql: str):
        """执行 SQL 查询"""
        if not sql:
            return [], []
        
        max_rows = int(self.env['ir.config_parameter'].sudo().get_param('ai_report.max_query_rows', 1000))
        if 'LIMIT' not in sql.upper():
            sql = sql.rstrip(';') + f' LIMIT {max_rows}'
        
        _logger.info(f"执行SQL: {sql}")
        
        try:
            self.env.cr.execute(sql)
            columns = [desc[0] for desc in self.env.cr.description]
            data = self.env.cr.fetchall()
            _logger.info(f"查询结果: columns={columns}, rows={data}")
            return columns, data
        except Exception as e:
            _logger.error(f"SQL执行失败: {e}")
            return [], []