# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging
import time
import uuid

_logger = logging.getLogger(__name__)


def _make_session_id():
    return 'session_' + uuid.uuid4().hex[:12]


class AiReportController(http.Controller):

    @http.route('/ai_report/chat', type='http', auth='public', csrf=False, methods=['GET', 'POST'])
    def chat(self, **kwargs):
        """处理聊天请求"""
        if not request.env.user or request.env.user.id == request.env.ref('base.public_user').id:
            return request.make_response(
                json.dumps({'type': 'error', 'message': '请先登录后再使用此功能', 'need_login': True}),
                headers={'Content-Type': 'application/json'}
            )
        
        _logger.info(f"[AI Report] /ai_report/chat called, method={request.httprequest.method}, user={request.env.user.name}")
        
        question = request.params.get('question', '')
        session_id = request.params.get('session_id', '')
        
        _logger.info(f"[AI Report] question from params: {question}")
        
        if not question and request.httprequest.method == 'POST':
            try:
                body_data = request.json()
                question = body_data.get('question', '')
                session_id = session_id or body_data.get('session_id', '')
                _logger.info(f"[AI Report] question from json body: {question}")
            except Exception as e:
                _logger.warning(f"request.json() failed: {e}")
                try:
                    body_data = json.loads(request.httprequest.data.decode('utf-8'))
                    question = body_data.get('question', '')
                    session_id = session_id or body_data.get('session_id', '')
                    _logger.info(f"[AI Report] question from raw data: {question}")
                except Exception as e2:
                    _logger.warning(f"raw data parse failed: {e2}")
        
        if not session_id:
            session_id = _make_session_id()
        
        _logger.info(f"[AI Report] final question={question}, session_id={session_id}")

        if not question.strip():
            return request.make_response(
                json.dumps({'type': 'error', 'message': '请输入问题', 'session_id': session_id}),
                headers={'Content-Type': 'application/json'}
            )

        _logger.info(f"AI Report: 收到问题: {question} session={session_id}")

        chat_model = request.env['ai.report.chat'].sudo()
        try:
            chat_model.save_chat(session_id, 'user', question, result_type='info')
        except Exception as e:
            _logger.warning(f"保存用户消息失败: {e}")

        try:
            _logger.info(f"[AI Report] ========== 开始处理问题 ==========")
            _logger.info(f"[AI Report] question: {question}")
            _logger.info(f"[AI Report] session_id: {session_id}")
            
            api_base = request.env['ir.config_parameter'].sudo().get_param('ai_report.llm_api_base', '')
            _logger.info(f"[AI Report] LLM API: {api_base}")
            
            if not api_base:
                return request.make_response(
                    json.dumps({'type': 'error', 'message': 'LLM API 未配置，请先在设置中配置'}),
                    headers={'Content-Type': 'application/json'}
                )
            
            chat2bi_model = request.env['ai.report.chat2bi']
            _logger.info(f"[AI Report] chat2bi_model: {chat2bi_model}")
            result = chat2bi_model.process_query(question, session_id=session_id)
            _logger.info(f"[AI Report] process_query 返回 type={result.get('type')}, has_sql={'sql' in result}")
            
            # SQL只在日志中输出，不返回给前端
            _logger.info(f"[AI Report] SQL: {result.get('sql', '')}")
            result_to_return = dict(result)
            result_to_return.pop('sql', None)
            
            if result.get('type') == 'error':
                _logger.warning(f"[AI Report] 处理返回错误: {result.get('message')}")
            
            try:
                chat_model.save_chat(
                    session_id,
                    'assistant',
                    result.get('explanation') or result.get('message') or '助手已回复',
                    result_type=result.get('type', 'query'),
                    result=result,
                    sql=result.get('sql'),
                    chart_type=result.get('chart_suggestion') or 'bar'
                )
            except Exception as save_err:
                _logger.warning(f"保存对话失败: {save_err}")
            
            _logger.info(f"[AI Report] ========== 处理完成 ==========")
            
            result_to_return['session_id'] = session_id
            return request.make_response(
                json.dumps(result_to_return, ensure_ascii=False),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
        except Exception as e:
            import traceback
            _logger.error(f"Chat2BI 处理失败: {e}")
            _logger.error(f"详细堆栈: {traceback.format_exc()}")
            error_result = {'type': 'error', 'message': f'处理失败: {str(e)}', 'session_id': session_id}
            try:
                chat_model.save_chat(session_id, 'assistant', str(e), result_type='error')
            except:
                pass
            return request.make_response(
                json.dumps(error_result, ensure_ascii=False),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )

    @http.route('/ai_report/health', type='http', auth='public')
    def health(self):
        """健康检查"""
        try:
            api_base = request.env['ir.config_parameter'].sudo().get_param(
                'ai_report.llm_api_base', ''
            )
            
            chat2bi_model = request.env['ai.report.chat2bi']
            _logger.info(f"[AI Report] health check - chat2bi_model: {chat2bi_model}")
            
            return http.Response(
                json.dumps({
                    'status': 'ok',
                    'llm_api': api_base or 'not_configured',
                    'module': 'ai_report',
                    'version': '3.0.0',
                    'chat2bi_available': bool(chat2bi_model)
                }),
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error(f"health check error: {e}")
            return http.Response(json.dumps({'status': 'error', 'message': str(e)}), mimetype='application/json')

    @http.route('/ai_report/debug', type='http', auth='user', csrf=False)
    def debug(self):
        """调试接口"""
        try:
            chat2bi = request.env['ai.report.chat2bi']
            _logger.info(f"[AI Report] debug - chat2bi: {chat2bi}")
            _logger.info(f"[AI Report] debug - chat2bi._name: {chat2bi._name}")
            
            result = chat2bi.process_query("测试", session_id="debug_test")
            _logger.info(f"[AI Report] debug result: {result}")
            
            return http.Response(json.dumps({'status': 'ok', 'result': str(result)}), mimetype='application/json')
        except Exception as e:
            import traceback
            _logger.error(f"debug error: {e}\n{traceback.format_exc()}")
            return http.Response(json.dumps({'status': 'error', 'message': str(e)}), mimetype='application/json')

    @http.route('/ai_report/sql', type='http', auth='user', csrf=False)
    def test_sql(self):
        """测试 SQL 查询"""
        _logger.info('[AI Report] /ai_report/sql called')
        
        # 测试1：今年各月销售额
        sql1 = """SELECT TO_CHAR(so.date_order, 'YYYY-MM') AS month, 
                  ROUND(CAST(SUM(sol.price_unit * sol.product_uom_qty) AS NUMERIC), 2) AS index 
           FROM sale_order_line sol 
           JOIN sale_order so ON sol.order_id = so.id 
           WHERE so.state IN ('sale', 'done') 
             AND EXTRACT(YEAR FROM so.date_order) = EXTRACT(YEAR FROM CURRENT_DATE)
           GROUP BY TO_CHAR(so.date_order, 'YYYY-MM')
           ORDER BY month"""
        
        # 测试2：产品销量排名 - 提取翻译字段的实际值
        sql2 = """SELECT 
                  COALESCE(pp.default_code, 
                    CASE 
                      WHEN pt.name::text LIKE '%{%' THEN 
                        COALESCE(pt.name->>'zh_CN', pt.name->>'en_US', 'Unknown')
                      ELSE pt.name::text
                    END, 'Unknown') AS product_name, 
                  SUM(sol.product_uom_qty) AS index 
           FROM sale_order_line sol 
           LEFT JOIN product_product pp ON sol.product_id = pp.id 
           LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id 
           LEFT JOIN sale_order so ON sol.order_id = so.id 
           WHERE so.state IN ('sale', 'done')
           GROUP BY COALESCE(pp.default_code, 
                    CASE 
                      WHEN pt.name::text LIKE '%{%' THEN 
                        COALESCE(pt.name->>'zh_CN', pt.name->>'en_US', 'Unknown')
                      ELSE pt.name::text
                    END)
           ORDER BY index DESC 
           LIMIT 10"""
        
        try:
            request.env.cr.execute(sql1)
            cols1 = [desc[0] for desc in request.env.cr.description]
            data1 = request.env.cr.fetchall()
            
            request.env.cr.execute(sql2)
            cols2 = [desc[0] for desc in request.env.cr.description]
            data2 = request.env.cr.fetchall()
            
            _logger.info(f'[AI Report] product_ranking result: cols={cols2}, data={data2}')
            
            return http.Response(
                json.dumps({
                    'monthly_sales': {'columns': cols1, 'data': [list(row) for row in data1]},
                    'product_ranking': {'columns': cols2, 'data': [list(row) for row in data2]}
                }),
                mimetype='application/json'
            )
        except Exception as e:
            import traceback
            _logger.error(f'[AI Report] SQL error: {e}\n{traceback.format_exc()}')
            return http.Response(json.dumps({'error': str(e)}), mimetype='application/json')

    @http.route('/ai_report', type='http', auth='public', website=True)
    def ai_report_page(self):
        """AI Report 主页面"""
        _logger.info('[AI Report] Rendering ai_report_chat_page')
        return request.render('ai_report.ai_report_chat_page')