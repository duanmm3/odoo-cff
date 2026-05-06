from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class InquiryRequestImportWizard(models.TransientModel):
    _name = 'inquiry.request.import.wizard'
    _description = '批量导入报价需求向导'

    import_data = fields.Text(
        string='导入数据',
        required=True,
        help='每行一条，格式: 产品型号, 数量'
    )

    def action_confirm_import(self):
        """确认导入并刷新列表"""
        self.ensure_one()
        
        if not self.import_data or not self.import_data.strip():
            raise ValidationError(_('导入数据不能为空'))
        
        created_count = 0
        lines = self.import_data.strip().split('\n')
        
        for line in lines:
            if not line or not line.strip():
                continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue
            
            product_name = parts[0]
            try:
                product_qty = float(parts[1])
            except:
                continue
            
            if product_name and product_qty > 0:
                self.env['inquiry.request'].create({
                    'product_name': product_name,
                    'product_qty': product_qty,
                    'salesperson_id': self.env.user.id,
                    'state': 'draft',
                })
                created_count += 1
        
        # 返回关闭弹窗并刷新列表
        return {
            'type': 'ir.actions.act_window_close',
        }