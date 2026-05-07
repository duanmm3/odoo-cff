from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from urllib.parse import quote_plus

_logger = logging.getLogger(__name__)

class InquiryQuote(models.Model):
    _name = 'inquiry.quote'
    _description = '采购报价'
    _order = 'create_date desc'
    _inherit = ['mail.thread']

    request_id = fields.Many2one(
        'inquiry.request',
        string='报价需求',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    request_partner_id = fields.Many2one(
        related='request_id.partner_id',
        string='客户',
        readonly=True
    )
    request_product_id = fields.Many2one(
        related='request_id.product_id',
        string='产品',
        readonly=True
    )
    request_product_name = fields.Char(
        related='request_id.product_name',
        string='产品型号',
        readonly=True
    )
    request_product_qty = fields.Float(
        related='request_id.product_qty',
        string='数量',
        readonly=True
    )
    request_salesperson_id = fields.Many2one(
        related='request_id.salesperson_id',
        string='销售员',
        readonly=True
    )
    supplier_code = fields.Char(
        string='供应商编码',
        compute='_compute_supplier_code',
        store=False
    )
    price_query_url = fields.Char(
        string='价格查询',
        compute='_compute_price_query_url',
        store=False
    )
    price_iframe = fields.Html(
        string='价格参考',
        sanitize=False,
        sanitize_attributes=False,
        compute='_compute_price_iframe',
        store=False
    )

    def _compute_price_query_url(self):
        for record in self:
            if record.request_id and record.request_id.product_name:
                model = quote_plus(record.request_id.product_name)
                record.price_query_url = f'/price/query/submit?ic_model={model}'
            else:
                record.price_query_url = False

    def _compute_price_iframe(self):
        for record in self:
            if not record.request_id:
                record.price_iframe = False
                continue
            
            model = record.request_id.product_name
            if not model:
                html = '''
<div style="padding: 20px; text-align: center; background: #fff3cd; color: #856404; border-radius: 5px;">
    <h4><i class="fa fa-warning"></i> 提示：需求单中未填写产品型号</h4>
    <p>请先在报价需求中填写产品型号，然后再进行报价。</p>
</div>
'''
                record.price_iframe = html
                continue
            
            encoded_model = quote_plus(model)
            html = f'''
<div class="price_tabs" style="border: 1px solid #ddd; border-radius: 5px;">
    <div style="display: flex; background: #f5f5f5; border-bottom: 1px solid #ddd; flex-wrap: wrap;">
        <button type="button" onclick="document.getElementById('tab_api').style.display='block';document.getElementById('tab_sht').style.display='none';document.getElementById('tab_yhxc').style.display='none';" style="flex: 1; min-width: 120px; padding: 12px; cursor: pointer; border: none; background: #007bff; color: white; font-weight: bold;">API报价</button>
        <button type="button" onclick="document.getElementById('tab_api').style.display='none';document.getElementById('tab_sht').style.display='block';document.getElementById('tab_yhxc').style.display='none';" style="flex: 1; min-width: 120px; padding: 12px; cursor: pointer; border: none; background: #f8f9fa; color: #333;">圣禾堂</button>
        <button type="button" onclick="document.getElementById('tab_api').style.display='none';document.getElementById('tab_sht').style.display='none';document.getElementById('tab_yhxc').style.display='block';" style="flex: 1; min-width: 120px; padding: 12px; cursor: pointer; border: none; background: #f8f9fa; color: #333;">云汉芯城</button>
        <button type="button" onclick="window.open('https://www.hqchip.com/search/{encoded_model}.html', '_blank')" style="flex: 1; min-width: 120px; padding: 12px; cursor: pointer; border: none; background: #f8f9fa; color: #333;">华秋商城</button>
        <button type="button" onclick="window.open('https://cn.brokerforum.com/electronic-components-search-zh.jsa?originalFullPartNumber={encoded_model}&hasNoSearchCriteria=false', '_blank')" style="flex: 1; min-width: 120px; padding: 12px; cursor: pointer; border: none; background: #f8f9fa; color: #333;">美迪瑞福</button>
    </div>
    <div id="tab_api" style="display: block; padding: 10px;">
        <iframe src="/price/query/submit?ic_model={encoded_model}" width="100%" height="600" style="border: none;"></iframe>
    </div>
    <div id="tab_sht" style="display: none; padding: 10px;">
        <iframe src="https://www.bomman.com/global-search?searchWord={encoded_model}&eventType=search" width="100%" height="600" style="border: none;"></iframe>
    </div>
    <div id="tab_yhxc" style="display: none; padding: 10px;">
        <iframe src="https://search.ickey.cn/?keyword={encoded_model}&bom_ab=null" width="100%" height="600" style="border: none;"></iframe>
    </div>
</div>
'''
            record.price_iframe = html

    def _compute_supplier_code(self):
        for record in self:
            if record.supplier_id:
                record.supplier_code = record.supplier_id.partner_code or record.supplier_id.name
            else:
                record.supplier_code = False
    buyer_id = fields.Many2one(
        'res.users',
        string='采购员',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    price = fields.Float(
        string='报价',
        tracking=True
    )
    supplier_name = fields.Char(
        string='供应商名称',
        tracking=True
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='供应商',
        domain=[('supplier_rank', '>', 0)],
        tracking=True
    )
    state = fields.Selection([
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('cancelled', '已取消')
    ], string='状态', default='submitted', tracking=True)
    remark = fields.Text(
        string='备注',
        tracking=True
    )

    @api.model
    def create(self, vals):
        if isinstance(vals, list):
            for val in vals:
                if val.get('supplier_id') and not val.get('supplier_name'):
                    supplier = self.env['res.partner'].browse(val['supplier_id'])
                    val['supplier_name'] = supplier.name
        elif isinstance(vals, dict):
            if vals.get('supplier_id') and not vals.get('supplier_name'):
                supplier = self.env['res.partner'].browse(vals['supplier_id'])
                vals['supplier_name'] = supplier.name
        
        records = super().create(vals)
        
        for record in records:
            if record.request_id and record.request_id.state == 'draft':
                record.request_id.write({'state': 'quoted'})
        
        return records

    def write(self, vals):
        if isinstance(vals, dict):
            if vals.get('supplier_id') and not vals.get('supplier_name'):
                supplier = self.env['res.partner'].browse(vals['supplier_id'])
                vals['supplier_name'] = supplier.name
        return super().write(vals)

    def action_cancel_quote(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return {'type': 'ir.actions.act_window_close'}

    def action_open_price_query(self):
        self.ensure_one()
        if self.request_id and self.request_id.product_name:
            model = quote_plus(self.request_id.product_name)
            url = f'/price/query/submit?ic_model={model}'
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        return {}

    def _get_buyer_domain(self):
        if self.env.is_superuser():
            return []
        if self.env.user.has_group('base.group_system'):
            return []
        if self.env.user.has_group('custom_price_module.group_inquiry_manager'):
            return []
        if self.env.user.has_group('purchase.group_purchase_user'):
            return [('buyer_id', '=', self.env.uid)]
        return []

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        user_domain = self._get_buyer_domain()
        if user_domain:
            domain = domain + user_domain
        return super()._search(domain, offset, limit, order, **kwargs)