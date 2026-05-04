# -*- coding: utf-8 -*-
"""DML Engine — DML 操作引擎"""

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class DMLEngine(models.AbstractModel):
    _name = 'ai.report.dml'
    _description = 'DML 操作引擎'

    @api.model
    def execute(self, intent_result: dict, question: str) -> dict:
        """执行 DML 操作"""
        intent = intent_result.get('intent', '')
        method_map = {
            'sale_create': 'create_sale_order',
            'sale_update': 'update_sale_order',
            'sale_delete': 'delete_sale_order',
            'purchase_create': 'create_purchase_order',
            'purchase_update': 'update_purchase_order',
            'purchase_delete': 'delete_purchase_order',
            'stock_in': 'stock_in',
            'stock_out': 'stock_out',
        }
        
        method = method_map.get(intent)
        if method and hasattr(self, method):
            return getattr(self, method)(intent_result, question)
        
        return {'success': False, 'message': f'未知操作: {intent}'}

    @api.model
    def create_sale_order(self, params: dict, question: str) -> dict:
        """创建销售订单"""
        try:
            partner_name = params.get('partner_name', '')
            partner_id = params.get('partner_id')
            
            if not partner_id and partner_name:
                partner = self.env['res.partner'].search([('name', 'ilike', partner_name)], limit=1)
                if not partner:
                    return {'success': False, 'message': f'未找到客户: {partner_name}'}
                partner_id = partner.id

            order_lines = []
            for line in params.get('lines', []):
                product_name = line.get('product_name', '')
                product_id = line.get('product_id')
                
                if not product_id and product_name:
                    product = self.env['product.product'].search([('name', 'ilike', product_name)], limit=1)
                    if not product:
                        return {'success': False, 'message': f'未找到产品: {product_name}'}
                    product_id = product.id

                order_lines.append((0, 0, {
                    'product_id': product_id,
                    'product_uom_qty': line.get('quantity', 1),
                }))

            order = self.env['sale.order'].create({
                'partner_id': partner_id,
                'order_line': order_lines,
            })

            return {
                'success': True,
                'message': f'已创建销售订单 {order.name}',
                'order_id': order.id,
                'order_name': order.name,
            }
        except Exception as e:
            _logger.error(f"ai_report: 创建销售订单失败 ({e})")
            return {'success': False, 'message': f'创建失败: {str(e)}'}

    @api.model
    def update_sale_order(self, params: dict, question: str) -> dict:
        """修改销售订单"""
        try:
            order_id = params.get('order_id')
            if not order_id:
                return {'success': False, 'message': '未指定订单ID'}
            
            order = self.env['sale.order'].browse(order_id)
            if not order.exists():
                return {'success': False, 'message': '订单不存在'}
            
            if order.state not in ('draft', 'sale'):
                return {'success': False, 'message': f'订单状态不支持修改: {order.state}'}
            
            update_vals = {}
            if params.get('partner_id'):
                update_vals['partner_id'] = params['partner_id']
            
            if update_vals:
                order.write(update_vals)
            
            return {'success': True, 'message': f'已更新销售订单 {order.name}'}
        except Exception as e:
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    @api.model
    def delete_sale_order(self, params: dict, question: str) -> dict:
        """删除销售订单"""
        try:
            order_id = params.get('order_id')
            if not order_id:
                return {'success': False, 'message': '未指定订单ID'}
            
            order = self.env['sale.order'].browse(order_id)
            if not order.exists():
                return {'success': False, 'message': '订单不存在'}
            
            if order.state not in ('draft', 'cancel'):
                return {'success': False, 'message': f'仅草稿/取消状态可删除: {order.state}'}
            
            name = order.name
            order.unlink()
            
            return {'success': True, 'message': f'已删除销售订单 {name}'}
        except Exception as e:
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    @api.model
    def create_purchase_order(self, params: dict, question: str) -> dict:
        """创建采购订单"""
        try:
            partner_name = params.get('partner_name', '')
            partner_id = params.get('partner_id')
            
            if not partner_id and partner_name:
                partner = self.env['res.partner'].search([
                    ('name', 'ilike', partner_name),
                    ('supplier_rank', '>', 0),
                ], limit=1)
                if not partner:
                    return {'success': False, 'message': f'未找到供应商: {partner_name}'}
                partner_id = partner.id

            order_lines = []
            for line in params.get('lines', []):
                product_name = line.get('product_name', '')
                product_id = line.get('product_id')
                
                if not product_id and product_name:
                    product = self.env['product.product'].search([('name', 'ilike', product_name)], limit=1)
                    product_id = product.id

                order_lines.append((0, 0, {
                    'product_id': product_id,
                    'product_qty': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                }))

            order = self.env['purchase.order'].create({
                'partner_id': partner_id,
                'order_line': order_lines,
            })

            return {
                'success': True,
                'message': f'已创建采购订单 {order.name}',
                'order_id': order.id,
                'order_name': order.name,
            }
        except Exception as e:
            return {'success': False, 'message': f'创建失败: {str(e)}'}

    @api.model
    def update_purchase_order(self, params: dict, question: str) -> dict:
        """修改采购订单"""
        try:
            order_id = params.get('order_id')
            if not order_id:
                return {'success': False, 'message': '未指定订单ID'}
            
            order = self.env['purchase.order'].browse(order_id)
            if not order.exists():
                return {'success': False, 'message': '订单不存在'}
            
            if order.state not in ('draft', 'sent'):
                return {'success': False, 'message': f'订单状态不支持修改: {order.state}'}
            
            update_vals = {}
            if params.get('partner_id'):
                update_vals['partner_id'] = params['partner_id']
            
            if update_vals:
                order.write(update_vals)
            
            return {'success': True, 'message': f'已更新采购订单 {order.name}'}
        except Exception as e:
            return {'success': False, 'message': f'更新失败: {str(e)}'}

    @api.model
    def delete_purchase_order(self, params: dict, question: str) -> dict:
        """删除采购订单"""
        try:
            order_id = params.get('order_id')
            if not order_id:
                return {'success': False, 'message': '未指定订单ID'}
            
            order = self.env['purchase.order'].browse(order_id)
            if not order.exists():
                return {'success': False, 'message': '订单不存在'}
            
            if order.state not in ('draft', 'cancel'):
                return {'success': False, 'message': f'仅草稿/取消状态可删除'}
            
            name = order.name
            order.unlink()
            
            return {'success': True, 'message': f'已删除采购订单 {name}'}
        except Exception as e:
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    @api.model
    def stock_in(self, params: dict, question: str) -> dict:
        """入库操作"""
        try:
            product_name = params.get('product_name', '')
            product_id = params.get('product_id')
            quantity = params.get('quantity', 1)
            
            if not product_id and product_name:
                product = self.env['product.product'].search([('name', 'ilike', product_name)], limit=1)
                if not product:
                    return {'success': False, 'message': f'未找到产品: {product_name}'}
                product_id = product.id

            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
            if not picking_type:
                return {'success': False, 'message': '未找到入库类型'}
            
            location_dest = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
            
            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': location_dest.id,
                'move_ids': [(0, 0, {
                    'name': product.display_name,
                    'product_id': product_id,
                    'product_uom_qty': quantity,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': location_dest.id,
                })],
            })
            
            picking.action_confirm()
            picking.action_assign()
            
            for move in picking.move_ids:
                move.quantity_done = quantity
            picking.button_validate()
            
            return {
                'success': True,
                'message': f'入库成功！调拨单: {picking.name}',
                'picking_id': picking.id,
            }
        except Exception as e:
            return {'success': False, 'message': f'入库失败: {str(e)}'}

    @api.model
    def stock_out(self, params: dict, question: str) -> dict:
        """出库操作"""
        try:
            product_name = params.get('product_name', '')
            product_id = params.get('product_id')
            quantity = params.get('quantity', 1)
            
            if not product_id and product_name:
                product = self.env['product.product'].search([('name', 'ilike', product_name)], limit=1)
                product_id = product.id

            picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
            if not picking_type:
                return {'success': False, 'message': '未找到出库类型'}
            
            location_src = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
            
            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': location_src.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                'move_ids': [(0, 0, {
                    'name': product.display_name,
                    'product_id': product_id,
                    'product_uom_qty': quantity,
                    'location_id': location_src.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                })],
            })
            
            picking.action_confirm()
            picking.action_assign()
            
            for move in picking.move_ids:
                move.quantity_done = quantity
            picking.button_validate()
            
            return {
                'success': True,
                'message': f'出库成功！调拨单: {picking.name}',
                'picking_id': picking.id,
            }
        except Exception as e:
            return {'success': False, 'message': f'出库失败: {str(e)}'}