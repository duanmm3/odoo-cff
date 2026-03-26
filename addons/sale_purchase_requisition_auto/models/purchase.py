# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    """
    扩展采购订单功能：
    1. 当采购员修改供应商时，自动将采购人更新为当前操作者
    2. 同步更新关联的采购需求单信息
    """
    _inherit = 'purchase.order'

    def write(self, vals):
        """
        重写write方法，实现自动更新采购人功能
        
        业务逻辑：
        - 当采购员（如Susan）修改供应商时，系统自动将采购人更新为当前操作者
        - 这解决了Susan修改供应商后因采购人仍是原采购员（Alan）而导致的权限问题
        - 同时同步更新关联的采购需求单（purchase.requisition）的供应商和采购人信息
        
        参数:
            vals: 写入字段的字典
            
        返回:
            super().write()的执行结果
        """
        # 【核心修复】当修改供应商但未指定采购人时，自动将采购人设为当前用户
        # 这确保了修改供应商的采购员自动成为该订单的负责人
        if 'partner_id' in vals and 'user_id' not in vals:
            vals = dict(vals)
            vals['user_id'] = self.env.user.id
        
        # 执行父类的write方法，完成正常的记录更新
        result = super(PurchaseOrder, self).write(vals)
        
        # 如果修改了供应商或采购人，同步更新关联的采购需求单
        if 'partner_id' in vals or 'user_id' in vals:
            for order in self:
                if order.requisition_id:
                    update_vals = {}
                    # 同步供应商信息到需求单
                    if 'partner_id' in vals:
                        update_vals['vendor_id'] = vals['partner_id']
                    # 同步采购人信息到需求单
                    if 'user_id' in vals:
                        update_vals['user_id'] = vals['user_id']
                    if update_vals:
                        # 使用sudo()以确保有权限更新需求单
                        order.requisition_id.sudo().write(update_vals)
        return result

    def button_confirm(self):
        """
        重写确认按钮方法
        
        当采购员确认订单时，将最终的供应商和采购人信息同步到需求单
        """
        for order in self:
            if order.requisition_id:
                order.requisition_id.sudo().write({
                    'vendor_id': order.partner_id.id,
                    'user_id': order.user_id.id,
                })
        return super(PurchaseOrder, self).button_confirm()
