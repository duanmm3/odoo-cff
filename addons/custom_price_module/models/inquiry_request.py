from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class InquiryRequest(models.Model):
    _name = 'inquiry.request'
    _description = '报价需求'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='报价需求流水号',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='客户编码',
        domain=[('customer_rank', '>', 0)],
        tracking=True
    )
    product_name = fields.Char(
        string='产品型号',
        tracking=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='产品',
        tracking=True
    )
    product_qty = fields.Float(
        string='数量',
        default=1.0,
        tracking=True
    )
    suggested_price = fields.Float(
        string='建议价格',
        tracking=True
    )
    salesperson_id = fields.Many2one(
        'res.users',
        string='销售员',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    state = fields.Selection([
        ('draft', '草稿'),
        ('quoted', '已报价'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消')
    ], string='状态', default='draft', tracking=True)

    lowest_quote_price = fields.Float(
        string='最低报价',
        compute='_compute_lowest_quote',
        store=True
    )
    lowest_quote_supplier = fields.Char(
        string='最低报价供应商',
        compute='_compute_lowest_quote',
        store=True
    )
    lowest_quote_supplier_code = fields.Char(
        string='最低报价供应商编码',
        compute='_compute_lowest_quote',
        store=True
    )
    lowest_quote_buyer = fields.Many2one(
        'res.users',
        string='最低报价采购员',
        compute='_compute_lowest_quote',
        store=True
    )

    quote_ids = fields.One2many(
        'inquiry.quote',
        'request_id',
        string='采购报价'
    )
    purchase_user_ids = fields.Many2many(
        'res.users',
        string='采购受理人',
        compute='_compute_purchase_users',
        store=False
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='销售报价单',
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='公司',
        default=lambda self: self.env.company,
        required=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if isinstance(vals, dict):
                if vals.get('name', _('New')) == _('New'):
                    vals['name'] = self.env['ir.sequence'].next_by_code('inquiry.request') or _('New')
        return super().create(vals_list)

    @api.depends('quote_ids')
    def _compute_lowest_quote(self):
        for record in self:
            active_quotes = record.quote_ids.filtered(lambda q: q.state == 'submitted' and q.price > 0)
            if active_quotes:
                lowest_quote = min(active_quotes, key=lambda q: q.price)
                record.lowest_quote_price = lowest_quote.price
                record.lowest_quote_supplier = lowest_quote.supplier_name
                if lowest_quote.supplier_id:
                    record.lowest_quote_supplier_code = lowest_quote.supplier_id.partner_code or lowest_quote.supplier_id.name
                else:
                    record.lowest_quote_supplier_code = False
                record.lowest_quote_buyer = lowest_quote.buyer_id
            else:
                record.lowest_quote_price = 0.0
                record.lowest_quote_supplier = False
                record.lowest_quote_supplier_code = False
                record.lowest_quote_buyer = False

    def _compute_purchase_users(self):
        users = self.env['res.users'].search([
            ('name', 'in', ['Cathy', 'Susan', 'Crystal', 'Sunny', 'Spring']),
            ('active', '=', True),
        ])
        for record in self:
            record.purchase_user_ids = users

    def action_confirm_request(self):
        self.ensure_one()
        if self.state != 'quoted':
            raise UserError(_('只有已报价状态的需求才能确认。'))

        if not self.lowest_quote_buyer:
            raise UserError(_('该需求暂无有效报价，无法确认！'))

        if not self.partner_id and not self.product_name:
            raise UserError(_('请先填写客户编码或产品型号！'))

        sale_order_vals = {
            'partner_id': self.partner_id.id if self.partner_id else False,
            'user_id': self.salesperson_id.id,
            'company_id': self.company_id.id,
            'origin': self.name,
        }

        sale_order = self.env['sale.order'].create(sale_order_vals)

        if self.product_id:
            sale_order_line_vals = {
                'order_id': sale_order.id,
                'product_id': self.product_id.id,
                'product_uom_qty': self.product_qty,
                'price_unit': self.lowest_quote_price,
            }
            self.env['sale.order.line'].create(sale_order_line_vals)
        elif self.product_name:
            default_product = self.env['product.product'].search([('type', '=', 'service')], limit=1)
            sale_order_line_vals = {
                'order_id': sale_order.id,
                'product_id': default_product.id if default_product else False,
                'name': self.product_name,
                'product_uom_qty': self.product_qty,
                'price_unit': self.lowest_quote_price,
            }
            self.env['sale.order.line'].create(sale_order_line_vals)

        self.write({
            'state': 'confirmed',
            'sale_order_id': sale_order.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel_request(self):
        self.ensure_one()
        if self.state == 'confirmed':
            raise UserError(_('已确认的需求不能取消。'))
        self.write({'state': 'cancelled'})

    def action_draft_request(self):
        self.ensure_one()
        if self.state == 'confirmed':
            raise UserError(_('已确认的需求不能重置为草稿。'))
        self.write({'state': 'draft'})

    def action_edit_request(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inquiry.request',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_unlink_request(self):
        self.ensure_one()
        if self.state == 'confirmed':
            raise UserError(_('已确认的需求不能删除！'))
        self.unlink()
        return {'type': 'ir.actions.act_window_close'}

    def action_open_quote_dialog(self):
        self.ensure_one()
        existing_quote = self.env['inquiry.quote'].search([
            ('request_id', '=', self.id),
            ('buyer_id', '=', self.env.uid),
        ], limit=1)

        if existing_quote:
            return {
                'type': 'ir.actions.act_window',
                'name': f'修改报价 - {self.name}',
                'res_model': 'inquiry.quote',
                'res_id': existing_quote.id,
                'view_mode': 'form',
                'target': 'new',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': f'提交报价 - {self.name}',
                'res_model': 'inquiry.quote',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_request_id': self.id,
                    'default_state': 'submitted',
                },
            }

    def action_view_all_quotes(self):
        self.ensure_one()
        quotes = self.quote_ids.filtered(lambda q: q.state != 'cancelled')
        if not quotes:
            raise UserError(_('该需求暂无采购报价记录。'))
        return {
            'type': 'ir.actions.act_window',
            'name': f'全部报价详情 - {self.name}',
            'res_model': 'inquiry.quote',
            'view_mode': 'list,form',
            'domain': [('request_id', '=', self.id), ('state', '!=', 'cancelled')],
            'target': 'new',
        }

    @api.constrains('product_qty')
    def _check_product_qty(self):
        for record in self:
            if record.product_qty <= 0:
                raise ValidationError(_('产品数量必须大于0。'))


class InquiryRequestImport(models.TransientModel):
    _name = 'inquiry.request.import'
    _description = '批量导入产品型号'

    data = fields.Text(
        string='导入数据',
        placeholder='格式1: 产品型号,数量\n格式2: 产品型号 产品型号,数量\n示例:\nCFF1,100\nCFF2 200\nSTM32,50'
    )

    def action_import(self):
        self.ensure_one()
        if not self.data:
            raise UserError(_('请输入导入数据。'))

        lines = self.data.strip().split('\n')
        imported_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 支持格式1: 产品型号,数量 或 格式2: 产品型号 产品型号,数量
            parts = line.replace('\t', ',').replace(' ', ',').split(',')
            
            # 如果只有一个部分，数量默认为1
            product_name = parts[0].strip()
            qty = float(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 1.0

            if product_name:
                self.env['inquiry.request'].create({
                    'product_name': product_name,
                    'product_qty': qty,
                    'salesperson_id': self.env.uid,
                })
                imported_count += 1

        return {
            'type': 'ir.actions.act_window_close',
            'infos': {'type': 'notification', 'title': '导入成功', 'message': f'已导入 {imported_count} 条记录'}
        }