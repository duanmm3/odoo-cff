# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
RFQ智能竞价通知系统
"""

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class PurchaseVendorQuoteHistory(models.Model):
    """采购报价历史记录"""
    _name = 'purchase.vendor.quote.history'
    _description = 'Vendor Quote History'
    _rec_name = 'vendor_id'

    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
        domain=[('supplier_rank', '>', 0)]
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    
    # 统计字段
    quote_count = fields.Integer(string='Quote Count', default=0)
    last_quote_date = fields.Datetime(string='Last Quote Date')
    last_quote_price = fields.Float(string='Last Quote Price')
    avg_price = fields.Float(string='Average Price')
    min_price = fields.Float(string='Minimum Price')
    max_price = fields.Float(string='Maximum Price')
    
    # 评分
    quote_score = fields.Float(
        string='Quote Score',
        compute='_compute_quote_score',
        store=True
    )

    @api.depends('quote_count', 'last_quote_date', 'avg_price')
    def _compute_quote_score(self):
        """计算报价评分：考虑报价次数和最近报价时间"""
        for record in self:
            if record.quote_count == 0:
                record.quote_score = 0
                continue
            
            # 基础分数：报价次数 * 10
            base_score = record.quote_count * 10
            
            # 时间衰减：30天内有报价得30分，每多一天减1分
            if record.last_quote_date:
                days_since = (datetime.now() - record.last_quote_date).days
                time_score = max(0, 30 - days_since)
            else:
                time_score = 0
            
            # 价格竞争力：历史最低价得20分
            if record.avg_price and record.min_price:
                price_score = 20 * (1 - (record.min_price / record.avg_price - 1))
                price_score = max(0, min(20, price_score))
            else:
                price_score = 0
            
            record.quote_score = base_score + time_score + price_score

    @api.model
    def update_quote_history(self, vendor_id, product_id, price, date_order=None):
        """更新报价历史"""
        history = self.search([
            ('vendor_id', '=', vendor_id),
            ('product_id', '=', product_id)
        ], limit=1)

        if not history:
            history = self.create({
                'vendor_id': vendor_id,
                'product_id': product_id,
                'quote_count': 1,
                'last_quote_date': date_order or fields.Datetime.now(),
                'last_quote_price': price,
                'avg_price': price,
                'min_price': price,
                'max_price': price,
            })
        else:
            # 更新统计
            new_count = history.quote_count + 1
            new_avg = (history.avg_price * history.quote_count + price) / new_count
            
            history.write({
                'quote_count': new_count,
                'last_quote_date': date_order or fields.Datetime.now(),
                'last_quote_price': price,
                'avg_price': new_avg,
                'min_price': min(history.min_price, price),
                'max_price': max(history.max_price, price),
            })
        
        return history

    @api.model
    def import_historical_data(self, data_list):
        """
        批量导入历史报价数据
        data_list: [{'vendor_id': 1, 'product_id': 2, 'price': 100, 'date': '2024-01-01'}, ...]
        """
        created_count = 0
        for data in data_list:
            self.create({
                'vendor_id': data.get('vendor_id'),
                'product_id': data.get('product_id'),
                'quote_count': data.get('quote_count', 1),
                'last_quote_date': data.get('date', fields.Datetime.now()),
                'last_quote_price': data.get('price'),
                'avg_price': data.get('price'),
                'min_price': data.get('price'),
                'max_price': data.get('price'),
            })
            created_count += 1
        return created_count

    def action_reset_quote_history(self):
        """重置报价历史"""
        self.unlink()
        return {
            'type': 'ir.actions.act_window_close',
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # 采购报价记录
    vendor_quote_history_id = fields.Many2one(
        'purchase.vendor.quote.history',
        string='Vendor Quote History',
        copy=False
    )


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # ==================== 智能竞价相关字段 ====================

    # RFQ状态
    quote_stage = fields.Selection([
        ('draft', 'Draft'),
        ('primary_contact', 'Primary Vendor Contacted'),
        ('bidding', 'Open for Bidding'),
        ('quoted', 'Received Quotes'),
        ('confirmed', 'Confirmed'),
    ], string='Quote Stage', default='draft', copy=False)

    # 优先采购 (从历史中选择)
    primary_vendor_id = fields.Many2one(
        'res.partner',
        string='Primary Vendor',
        copy=False,
        help='优先通知的供应商，基于历史报价'
    )

    # 超时设置 (小时)
    quote_timeout = fields.Integer(
        string='Quote Timeout (Hours)',
        default=24,
        help='等待优先供应商报价的小时数'
    )

    # 通知时间
    primary_notified_at = fields.Datetime(
        string='Primary Vendor Notified At',
        copy=False
    )
    
    # 竞价开始时间
    bidding_started_at = fields.Datetime(
        string='Bidding Started At',
        copy=False
    )

    # 收到的报价
    quote_ids = fields.One2many(
        'purchase.order.quote',
        'order_id',
        string='Quotes'
    )

    # 最佳报价
    best_quote_id = fields.Many2one(
        'purchase.order.quote',
        string='Best Quote',
        compute='_compute_best_quote',
        store=True
    )

    @api.depends('quote_ids.price_total')
    def _compute_best_quote(self):
        """计算最佳报价"""
        for order in self:
            if order.quote_ids:
                order.best_quote_id = min(
                    order.quote_ids,
                    key=lambda q: q.price_total
                ).id
            else:
                order.best_quote_id = False

    # ==================== 智能通知逻辑 ====================

    def action_notify_primary_vendor(self):
        """通知优先采购供应商"""
        self.ensure_one()
        
        if not self.primary_vendor_id:
            self._assign_primary_vendor()
        
        if not self.primary_vendor_id:
            raise UserError(_('未找到合适的供应商'))
        
        # 发送通知
        self._send_vendor_notification(self.primary_vendor_id)
        
        self.write({
            'quote_stage': 'primary_contact',
            'primary_notified_at': fields.Datetime.now(),
        })
        
        return True

    def _assign_primary_vendor(self):
        """分配优先供应商 - 基于历史报价"""
        self.ensure_one()
        
        # 获取订单中的产品
        products = self.order_line.mapped('product_id')
        if not products:
            return
        
        # 查找有历史报价的供应商
        vendor_scores = {}
        
        for product in products:
            histories = self.env['purchase.vendor.quote.history'].search([
                ('product_id', '=', product.id),
                ('quote_count', '>', 0),
            ], order='quote_score desc', limit=5)
            
            for history in histories:
                vendor_id = history.vendor_id.id
                if vendor_id not in vendor_scores:
                    vendor_scores[vendor_id] = 0
                vendor_scores[vendor_id] += history.quote_score
        
        if vendor_scores:
            # 选择评分最高的供应商
            best_vendor_id = max(vendor_scores, key=vendor_scores.get)
            self.write({'primary_vendor_id': best_vendor_id})

    def _send_vendor_notification(self, vendor_id):
        """发送供应商通知"""
        self.ensure_one()
        
        vendor = self.env['res.partner'].browse(vendor_id)
        
        # 创建询价消息
        self.message_post(
            body=_(
                '已向供应商 %s 发送询价请求，请尽快报价。'
            ) % vendor.name,
            subject=_('新询价单: %s') % self.name,
            partner_ids=[vendor.id]
        )

    def action_start_bidding(self):
        """开始公开竞价 - 通知所有供应商"""
        self.ensure_one()
        
        # 获取所有相关供应商
        vendors = self._get_available_vendors()
        
        if not vendors:
            raise UserError(_('未找到可用的供应商'))
        
        # 通知所有供应商
        for vendor in vendors:
            self._send_vendor_notification(vendor.id)
        
        self.write({
            'quote_stage': 'bidding',
            'bidding_started_at': fields.Datetime.now(),
        })
        
        return True

    def _get_available_vendors(self):
        """获取可用供应商 - 订单中产品的供应商"""
        self.ensure_one()
        
        products = self.order_line.mapped('product_id')
        
        # 获取所有相关产品的供应商
        vendor_ids = set()
        for product in products:
            seller_ids = product.seller_ids.filtered(
                lambda s: s.active and (not s.company_id or s.company_id == self.company_id)
            ).mapped('partner_id')
            vendor_ids.update(seller_ids.ids)
        
        return self.env['res.partner'].browse(list(vendor_ids))

    def action_check_quote_timeout(self):
        """检查报价超时 - 由定时任务调用"""
        orders = self.search([
            ('quote_stage', '=', 'primary_contact'),
            ('primary_notified_at', '!=', False),
        ])
        
        for order in orders:
            if not order.primary_notified_at:
                continue
            
            timeout = timedelta(hours=order.quote_timeout)
            elapsed = fields.Datetime.now() - order.primary_notified_at
            
            if elapsed > timeout:
                # 超时，开始公开竞价
                order.action_start_bidding()

    # ==================== 报价记录 ====================

    def write(self, vals):
        """监控报价，更新历史记录"""
        result = super().write(vals)
        
        # 如果订单确认，更新报价历史
        if vals.get('state') == 'purchase':
            self._update_quote_history()
        
        return result

    def _update_quote_history(self):
        """更新报价历史"""
        for order in self:
            for line in order.order_line:
                if line.price_unit and line.product_id:
                    self.env['purchase.vendor.quote.history'].update_quote_history(
                        vendor_id=order.partner_id.id,
                        product_id=line.product_id.id,
                        price=line.price_unit,
                        date_order=order.date_order
                    )

    def action_create_quote_record(self):
        """为当前RFQ创建报价记录"""
        self.ensure_one()
        
        # 检查是否已有报价记录
        if self.quote_ids.filtered(lambda q: q.vendor_id == self.partner_id):
            raise UserError(_('已存在该供应商的报价记录'))
        
        # 创建报价记录
        quote = self.env['purchase.order.quote'].create({
            'order_id': self.id,
            'vendor_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
        })
        
        # 创建报价明细 (从订单行复制)
        for line in self.order_line:
            if line.display_type:
                continue
            self.env['purchase.order.quote.line'].create({
                'quote_id': quote.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom.id,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
                'currency_id': self.currency_id.id,
            })
        
        # 更新RFQ状态
        self.write({'quote_stage': 'quoted'})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.quote',
            'res_id': quote.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_select_quote(self):
        """选择报价并确认订单"""
        self.ensure_one()
        
        # 选择最佳报价
        if not self.best_quote_id:
            raise UserError(_('没有可用的报价'))
        
        quote = self.best_quote_id
        
        # 更新订单明细为报价价格
        for line in self.order_line:
            quote_line = quote.quote_line_ids.filtered(
                lambda l: l.product_id == line.product_id
            )
            if quote_line:
                line.write({
                    'price_unit': quote_line.price_unit,
                    'tax_ids': [(6, 0, quote_line.tax_ids.ids)],
                })
        
        # 更新状态
        self.write({
            'quote_stage': 'confirmed',
            'partner_id': quote.vendor_id.id,
        })
        
        return True


class PurchaseOrderQuote(models.Model):
    """采购报价记录"""
    _name = 'purchase.order.quote'
    _description = 'Purchase Order Quote'
    _order = 'price_total asc'

    order_id = fields.Many2one(
        'purchase.order',
        string='RFQ',
        required=True,
        ondelete='cascade'
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True,
        domain=[('supplier_rank', '>', 0)]
    )
    
    # 报价明细
    quote_line_ids = fields.One2many(
        'purchase.order.quote.line',
        'quote_id',
        string='Quote Lines'
    )
    
    # 报价金额
    price_subtotal = fields.Monetary(
        string='Untaxed Amount',
        compute='_compute_amounts',
        store=True
    )
    price_tax = fields.Monetary(
        string='Tax',
        compute='_compute_amounts',
        store=True
    )
    price_total = fields.Monetary(
        string='Total Amount',
        compute='_compute_amounts',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    # 报价时间
    quoted_at = fields.Datetime(
        string='Quoted At',
        default=fields.Datetime.now
    )
    
    # 备注
    note = fields.Text(string='Notes')

    @api.depends('quote_line_ids.price_subtotal', 'quote_line_ids.price_tax')
    def _compute_amounts(self):
        """计算报价金额"""
        for quote in self:
            subtotal = sum(quote.quote_line_ids.mapped('price_subtotal'))
            tax = sum(quote.quote_line_ids.mapped('price_tax'))
            quote.price_subtotal = subtotal
            quote.price_tax = tax
            quote.price_total = subtotal + tax


class PurchaseOrderQuoteLine(models.Model):
    """报价明细"""
    _name = 'purchase.order.quote.line'
    _description = 'Purchase Quote Line'

    quote_id = fields.Many2one(
        'purchase.order.quote',
        string='Quote',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_qty = fields.Float(
        string='Quantity',
        required=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True
    )
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes'
    )
    
    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )
    price_tax = fields.Monetary(
        string='Tax',
        compute='_compute_subtotal',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    @api.depends('price_unit', 'product_qty', 'tax_ids')
    def _compute_subtotal(self):
        """计算小计"""
        for line in self:
            taxes = line.tax_ids.compute_all(
                line.price_unit,
                line.currency_id,
                line.product_qty,
                product=line.product_id
            )
            line.price_subtotal = taxes['total_excluded']
            line.price_tax = taxes['total_included'] - taxes['total_excluded']
