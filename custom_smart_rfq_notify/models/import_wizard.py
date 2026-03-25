# Part of Odoo. See LICENSE file for full copyright and licensing settings
"""
历史数据导入向导
"""

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.mimetypes import guess_mimetype
import base64
import csv
import io


class ImportQuoteHistoryWizard(models.TransientModel):
    """历史报价数据导入向导"""
    _name = 'import.quote.history.wizard'
    _description = 'Import Quote History Wizard'

    import_file = fields.Binary(
        string='Import File',
        required=True,
        help='支持CSV或XLS格式'
    )
    file_name = fields.Char(string='File Name')
    
    # 导入预览
    preview_ids = fields.One2many(
        'import.quote.history.line',
        'wizard_id',
        string='Preview'
    )
    
    import_mode = fields.Selection([
        ('create', 'Create Only'),
        ('update', 'Update Only'),
        ('create_update', 'Create and Update'),
    ], default='create_update', string='Import Mode')

    def action_import_file(self):
        """导入文件并预览"""
        self.ensure_one()
        
        if not self.import_file:
            raise UserError(_('请先选择要导入的文件'))
        
        # 解析文件
        try:
            data = self._parse_file()
        except Exception as e:
            raise UserError(_('文件解析失败: %s') % str(e))
        
        # 预览数据
        self._preview_data(data)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.quote.history.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def _parse_file(self):
        """解析CSV/XLS文件"""
        self.ensure_one()
        
        # 解码文件
        file_data = base64.b64decode(self.import_file)
        
        # 尝试CSV解析
        try:
            content = file_data.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
            
            data = []
            for row in rows:
                # 查找供应商
                vendor_name = row.get('vendor_name') or row.get('vendor') or row.get('supplier')
                vendor = self._find_vendor(vendor_name)
                
                # 查找产品
                product_name = row.get('product_name') or row.get('product') or row.get('item')
                product = self._find_product(product_name)
                
                if vendor and product:
                    data.append({
                        'vendor_id': vendor.id,
                        'product_id': product.id,
                        'vendor_name': vendor.name,
                        'product_name': product.name,
                        'price': float(row.get('price', 0) or 0),
                        'quote_count': int(row.get('quote_count', 1) or 1),
                    })
            
            return data
            
        except Exception as e:
            raise UserError(_('CSV解析失败: %s') % str(e))

    def _find_vendor(self, name):
        """查找供应商"""
        if not name:
            return False
        
        partner = self.env['res.partner'].search([
            ('name', 'ilike', name),
            ('supplier_rank', '>', 0)
        ], limit=1)
        
        return partner

    def _find_product(self, name):
        """查找产品"""
        if not name:
            return False
        
        product = self.env['product.product'].search([
            ('name', 'ilike', name)
        ], limit=1)
        
        if not product:
            # 尝试搜索 default_code
            product = self.env['product.product'].search([
                ('default_code', 'ilike', name)
            ], limit=1)
        
        return product

    def _preview_data(self, data):
        """预览导入数据"""
        self.ensure_one()
        
        # 清除旧预览
        self.preview_ids.unlink()
        
        # 创建预览行 (最多显示10条)
        for item in data[:10]:
            self.env['import.quote.history.line'].create({
                'wizard_id': self.id,
                'vendor_id': item['vendor_id'],
                'product_id': item['product_id'],
                'vendor_name': item['vendor_name'],
                'product_name': item['product_name'],
                'price': item['price'],
                'quote_count': item['quote_count'],
            })

    def action_confirm_import(self):
        """确认导入"""
        self.ensure_one()
        
        # 获取所有预览数据
        preview_data = self.preview_ids.read()
        
        if not preview_data:
            raise UserError(_('没有可导入的数据'))
        
        # 导入数据
        created = 0
        updated = 0
        
        for line in self.preview_ids:
            # 查找是否已存在
            existing = self.env['purchase.vendor.quote.history'].search([
                ('vendor_id', '=', line.vendor_id.id),
                ('product_id', '=', line.product_id.id),
            ])
            
            if existing:
                if self.import_mode in ('update', 'create_update'):
                    existing.write({
                        'last_quote_price': line.price,
                        'quote_count': line.quote_count,
                        'last_quote_date': fields.Datetime.now(),
                    })
                    updated += 1
            else:
                if self.import_mode in ('create', 'create_update'):
                    self.env['purchase.vendor.quote.history'].create({
                        'vendor_id': line.vendor_id.id,
                        'product_id': line.product_id.id,
                        'last_quote_price': line.price,
                        'quote_count': line.quote_count,
                        'avg_price': line.price,
                        'min_price': line.price,
                        'max_price': line.price,
                        'last_quote_date': fields.Datetime.now(),
                    })
                    created += 1
        
        # 提示结果
        message = f'导入完成！创建: {created} 条, 更新: {updated} 条'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('导入结果'),
                'message': message,
                'type': 'success',
            }
        }


class ImportQuoteHistoryLine(models.TransientModel):
    """导入预览行"""
    _name = 'import.quote.history.line'
    _description = 'Import Quote History Line'

    wizard_id = fields.Many2one(
        'import.quote.history.wizard',
        string='Wizard',
        required=True
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    vendor_name = fields.Char(string='Vendor Name')
    product_name = fields.Char(string='Product Name')
    price = fields.Float(string='Price')
    quote_count = fields.Integer(string='Quote Count')
    import_status = fields.Selection([
        ('ready', 'Ready'),
        ('skip', 'Skip'),
        ('error', 'Error'),
    ], compute='_compute_status', store=True)

    @api.depends('vendor_id', 'product_id')
    def _compute_status(self):
        """计算导入状态"""
        for line in self:
            if not line.vendor_id or not line.product_id:
                line.import_status = 'error'
            else:
                line.import_status = 'ready'


class ManualQuoteHistoryWizard(models.TransientModel):
    """手动添加报价历史向导"""
    _name = 'manual.quote.history.wizard'
    _description = 'Manual Quote History Wizard'

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
    price = fields.Float(string='Quote Price', required=True)
    quote_date = fields.Datetime(
        string='Quote Date',
        default=fields.Datetime.now
    )

    def action_add(self):
        """添加报价历史"""
        self.ensure_one()
        
        # 查找是否已存在
        existing = self.env['purchase.vendor.quote.history'].search([
            ('vendor_id', '=', self.vendor_id.id),
            ('product_id', '=', self.product_id.id),
        ])
        
        if existing:
            # 更新现有记录
            new_count = existing.quote_count + 1
            new_avg = (existing.avg_price * existing.quote_count + self.price) / new_count
            
            existing.write({
                'quote_count': new_count,
                'last_quote_price': self.price,
                'last_quote_date': self.quote_date,
                'avg_price': new_avg,
                'min_price': min(existing.min_price, self.price),
                'max_price': max(existing.max_price, self.price),
            })
            message = '报价历史已更新'
        else:
            # 创建新记录
            self.env['purchase.vendor.quote.history'].create({
                'vendor_id': self.vendor_id.id,
                'product_id': self.product_id.id,
                'last_quote_price': self.price,
                'quote_count': 1,
                'last_quote_date': self.quote_date,
                'avg_price': self.price,
                'min_price': self.price,
                'max_price': self.price,
            })
            message = '报价历史已添加'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'type': 'success',
            }
        }
