# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    """
    扩展 res.partner 模型
    - 添加客户/供应商相关字段
    - 实现基于 shared_users 的数据权限控制
    """
    _inherit = "res.partner"

    # =========================================================
    # 字段定义
    # =========================================================

    # 客户/供应商标记
    partner_type = fields.Selection([
        ('customer', '客户'),
        ('supplier', '供应商'),
        ('both', '客户和供应商'),
        ('other', '其他')
    ], string='客户/供应商标记', default='other', required=True)
    
    # 客户类型
    customer_type = fields.Selection([
        ('CF', '国内工厂 (CF)'),
        ('CT', '国内贸易 (CT)'),
        ('OF', '国外工厂 (OF)'),
        ('OT', '国外贸易 (OT)')
    ], string='客户类型')
    
    # 供应商类型
    supplier_type = fields.Selection([
        ('ST', '贸易 (ST)'),
        ('SF', '工厂 (SF)'),
        ('SD', '代理 (SD)'),
        ('SE', '呆滞 (SE)')
    ], string='供应商类型')
    
    # 客户/供应商代码
    partner_code = fields.Char(string='Code', readonly=True, copy=False, index=True)
    customer_grade = fields.Char(string='客户等级')
    customer_source = fields.Selection([
        ('1', '展会'),
        ('2', '互联网'),
        ('3', '广告')
    ], string='客户来源')
    reconciliation_day = fields.Selection([
        (str(i), str(i)) for i in range(1, 32)
    ], string='对账日 (每月)')
    english_name = fields.Char(string='英文名字')
    company_phone = fields.Char(string='公司电话')
    mobile_phone = fields.Char(string='移动电话')
    customer_tags = fields.Char(string='客户标签')
    tax_rate = fields.Selection([
        ('0.1300', '13%'),
        ('0', '0%')
    ], string='税率', default='0.1300')
    is_potential_customer = fields.Boolean(string='潜在客户', default=False)
    customer_currency = fields.Selection([
        ('USD', 'USD'),
        ('CNY', 'CNY'),
        ('HKD', 'HKD')
    ], string='客户货币', default='CNY')
    payment_method = fields.Selection([
        ('100_prepaid', '100%预付'),
        ('50_prepaid', '50%预付'),
        ('cash', '现金')
    ], string='付款方式')
    invoice_day = fields.Selection([
        (str(i), str(i)) for i in range(1, 32)
    ], string='开票日 (每月)')
    website = fields.Char(string='公司网址')
    
    # 共享销售/采购（多对多关系）
    # 用于权限控制：只有创建者或共享列表中的用户可以访问该联系人
    shared_users = fields.Many2many(
        'res.users',
        'partner_shared_users_rel',
        'partner_id',
        'user_id',
        string='共享销售/采购',
        help='可多选内部用户（销售、采购、管理员等）'
    )
    
    # 文件上传字段
    business_card = fields.Binary(string='名片')
    business_card_filename = fields.Char(string='名片文件名')
    business_license = fields.Binary(string='营业执照')
    business_license_filename = fields.Char(string='营业执照文件名')
    registration_certificate = fields.Binary(string='商业登记证/注册证书')
    registration_certificate_filename = fields.Char(string='登记证书文件名')
    payment_account = fields.Binary(string='付款账号/收款账号')
    payment_account_filename = fields.Char(string='账号文件名')
    survey_form = fields.Binary(string='客户情况调查表/供应商情况调查表')
    survey_form_filename = fields.Char(string='调查表文件名')
    
    # =========================================================
    # 约束和方法
    # =========================================================

    @api.constrains('partner_type', 'customer_type', 'supplier_type')
    def _check_partner_type_consistency(self):
        """自动设置客户类型和供应商类型的默认值"""
        for partner in self:
            if partner.partner_type in ['customer', 'both'] and not partner.customer_type:
                partner.customer_type = 'CF'
            if partner.partner_type in ['supplier', 'both'] and not partner.supplier_type:
                partner.supplier_type = 'ST'
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        创建联系人时的钩子方法
        
        功能说明：
        - 自动生成联系人代码（partner_code）
        - 自动设置客户类型/供应商类型的默认值
        - 自动将创建者添加到 shared_users（确保创建者可以访问自己创建的记录）
        """
        uid = self.env.uid
        for vals in vals_list:
            # 自动生成代码
            if 'partner_code' not in vals or not vals.get('partner_code'):
                vals['partner_code'] = self._generate_partner_code(vals)
            
            # 自动设置默认值
            partner_type = vals.get('partner_type', 'other')
            if partner_type in ['customer', 'both'] and 'customer_type' not in vals:
                vals['customer_type'] = 'CF'
            if partner_type in ['supplier', 'both'] and 'supplier_type' not in vals:
                vals['supplier_type'] = 'ST'
            
            # 自动将自己添加到 shared_users（权限控制关键步骤）
            if uid and 'shared_users' not in vals:
                vals['shared_users'] = [(6, 0, [uid])]
        
        return super(ResPartner, self).create(vals_list)
    
    def write(self, vals):
        """
        更新联系人时的钩子方法
        
        功能说明：
        - 当客户类型或供应商类型变化时，自动更新联系人代码
        """
        # 处理客户类型变化
        if 'partner_type' in vals:
            partner_type = vals.get('partner_type')
            if partner_type in ['customer', 'both'] and 'customer_type' not in vals:
                for partner in self:
                    if not partner.customer_type:
                        vals['customer_type'] = 'CF'
                        break
            if partner_type in ['supplier', 'both'] and 'supplier_type' not in vals:
                for partner in self:
                    if not partner.supplier_type:
                        vals['supplier_type'] = 'ST'
                        break
        
        result = super(ResPartner, self).write(vals)
        
        # 当类型变化时更新代码
        if 'customer_type' in vals or 'supplier_type' in vals or 'partner_type' in vals:
            for partner in self:
                current_vals = {
                    'partner_type': partner.partner_type,
                    'customer_type': partner.customer_type,
                    'supplier_type': partner.supplier_type,
                }
                new_code = self._generate_partner_code(current_vals)
                # 直接用 SQL 更新，避免递归
                self._cr.execute(
                    "UPDATE res_partner SET partner_code = %s WHERE id = %s",
                    (new_code, partner.id)
                )
        
        return result
    
    def _generate_partner_code(self, vals):
        """
        根据类型生成联系人代码
        
        代码规则：
        - 客户：CF/CF/CT/OT + 序号（如 CF00001）
        - 供应商：ST/SF/SD/SE + 序号
        - 其他：OTH + 序号
        """
        partner_type = vals.get('partner_type', 'other')
        
        # 根据类型确定前缀
        if partner_type == 'both':
            if vals.get('customer_type'):
                prefix = vals.get('customer_type', 'CF')
            else:
                prefix = vals.get('supplier_type', 'ST')
        elif partner_type in ['customer', 'both']:
            prefix = vals.get('customer_type', 'CF')
        elif partner_type in ['supplier']:
            prefix = vals.get('supplier_type', 'ST')
        else:
            prefix = 'OTH'
        
        # 查找最大序号
        existing_codes = self.env['res.partner'].sudo().search([]).mapped('partner_code')
        numbers = []
        for code in existing_codes:
            if code and code.startswith(prefix):
                try:
                    numbers.append(int(code[len(prefix):]))
                except ValueError:
                    continue
        
        next_num = max(numbers) + 1 if numbers else 1
        return f"{prefix}{next_num:05d}"
    
    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """当客户类型变化时，自动设置子类型默认值"""
        for record in self:
            if record.partner_type in ['customer', 'both'] and not record.customer_type:
                record.customer_type = 'CF'
            if record.partner_type in ['supplier', 'both'] and not record.supplier_type:
                record.supplier_type = 'ST'

    # =========================================================
    # 权限控制核心方法
    # =========================================================

    @api.model
    def _is_admin(self):
        """
        判断当前用户是否为管理员
        检查用户是否属于以下管理员组之一:
        - base.group_erp_manager (id=2)
        - base.group_system (id=4)
        - 本地管理员组 (id=24, 30, 35, 44)
        """
        uid = self.env.uid
        if not uid:
            return False
        
        if uid == 2:
            return True
        
        try:
            admin_group_ids = [2, 4, 24, 30, 35, 44]
            admin_groups = self.env['res.groups'].sudo().search([
                ('id', 'in', admin_group_ids)
            ])
            for group in admin_groups:
                if uid in group.users.ids:
                    return True
            return False
        except Exception:
            return False

    @api.model
    def _clean_domain(self, domain):
        """清理搜索条件，确保所有元素都是可哈希的"""
        if not domain:
            return []
        
        if hasattr(domain, '__domain__'):
            domain = domain.__domain__
        
        def _to_hashable(item):
            if isinstance(item, list):
                if len(item) == 0:
                    return ()
                return tuple(_to_hashable(i) for i in item)
            return item
        
        def _is_valid_clause(clause):
            if not isinstance(clause, (list, tuple)):
                return True
            if len(clause) == 0:
                return False
            if len(clause) >= 1 and isinstance(clause[0], (list, tuple)):
                return _is_valid_clause(clause[0])
            return True
        
        result = _to_hashable(domain)
        if isinstance(result, (list, tuple)) and len(result) == 1 and isinstance(result[0], (list, tuple)) and len(result[0]) == 0:
            return []
        
        return result

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        """搜索方法 - 权限控制入口"""
        uid = self.env.uid
        
        if not uid or self._is_admin():
            return super().search(domain, offset=offset, limit=limit, order=order)
        
        perm_domain = ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])]
        
        cleaned_domain = self._clean_domain(domain)
        if cleaned_domain:
            final_domain = ['&'] + perm_domain + list(cleaned_domain)
        else:
            final_domain = perm_domain
        
        return super().search(final_domain, offset=offset, limit=limit, order=order)

    @api.model
    def search_fetch(self, domain, field_names=None, offset=0, limit=None, order=None):
        """
        搜索获取方法 - 权限过滤
        
        注意: 此方法在search()和search_read()中被调用
        我们使用super().search()而不是search_fetch来避免潜在问题
        """
        uid = self.env.uid
        
        if not uid or self._is_admin():
            return super().search_fetch(domain, field_names, offset=offset, limit=limit, order=order)
        
        perm_domain = ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])]
        
        cleaned_domain = self._clean_domain(domain)
        if cleaned_domain:
            final_domain = ['&'] + perm_domain + list(cleaned_domain)
        else:
            final_domain = perm_domain
        
        return super().search_fetch(final_domain, field_names, offset=offset, limit=limit, order=order)

    @api.model
    def search_count(self, domain, limit=None):
        """搜索统计方法"""
        # 管理员：不过滤
        if self._is_admin():
            return super().search_count(domain, limit=limit)
        
        uid = self.env.uid
        if not uid:
            return super().search_count(domain, limit=limit)
        
        perm_domain = ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])]
        
        cleaned_domain = self._clean_domain(domain)
        if cleaned_domain:
            final_domain = ['&'] + perm_domain + list(cleaned_domain)
        else:
            final_domain = perm_domain
        
        return super().search_count(final_domain, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        搜索读取方法 - 手动应用权限过滤
        
        由于父类search_read内部调用search_fetch可能不经过我们的override，
        我们直接使用search方法获取ID再读取数据
        """
        if domain is None:
            domain = []
        
        uid = self.env.uid
        
        if not uid or self._is_admin():
            return super().search_read(domain, fields, offset, limit, order)
        
        perm_domain = ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])]
        cleaned_domain = self._clean_domain(domain)
        if cleaned_domain:
            final_domain = ['&'] + perm_domain + list(cleaned_domain)
        else:
            final_domain = perm_domain
        
        records = self.search(final_domain, offset=offset, limit=limit, order=order)
        
        if not records:
            return []
        
        return records.read(fields)

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        """
        Web search_read方法 - 手动应用权限过滤
        
        由于web_search_read内部调用search_fetch，我们需要确保权限过滤生效
        """
        uid = self.env.uid
        
        if not uid or self._is_admin():
            return super().web_search_read(domain, specification, offset, limit, order, count_limit)
        
        perm_domain = ['|', ('create_uid', '=', uid), ('shared_users', 'in', [uid])]
        cleaned_domain = self._clean_domain(domain)
        if cleaned_domain:
            final_domain = ['&'] + perm_domain + list(cleaned_domain)
        else:
            final_domain = perm_domain
        
        records = self.search(final_domain, offset=offset, limit=limit, order=order)
        
        if not records:
            return {'records': [], 'length': 0}
        
        values = records.web_read(specification)
        return {
            'records': values,
            'length': len(records),
        }

    def read(self, fields=None, load='_classic_read'):
        """
        读取方法 - 过滤无权限的记录
        
        注意：此方法主要用于二次防护，主要权限控制在 ir.rule 中完成
        """
        # 新建记录时（无ID），调用父类
        if not self.ids:
            return super().read(fields, load)
        
        # 管理员：不过滤
        if self._is_admin():
            return super().read(fields, load)
        
        # 如果没有uid，调用父类
        uid = self.env.uid
        if not uid:
            return super().read(fields, load)
        
        # 如果只有少量记录（可能是内部调用），直接调用父类
        # 主要的权限过滤已经在 ir.rule 中完成
        if len(self.ids) <= 5:
            return super().read(fields, load)
        
        # 对于大量记录，只过滤掉明显无权限的记录
        valid_ids = []
        for rid in self.ids:
            try:
                self._cr.execute("SELECT create_uid FROM res_partner WHERE id = %s", (rid,))
                row = self._cr.fetchone()
                if not row:
                    valid_ids.append(rid)
                    continue
                create_uid = row[0]
                
                self._cr.execute(
                    "SELECT 1 FROM partner_shared_users_rel WHERE partner_id = %s AND user_id = %s",
                    (rid, uid)
                )
                is_shared = self._cr.fetchone() is not None
                
                if create_uid == uid or is_shared:
                    valid_ids.append(rid)
            except:
                valid_ids.append(rid)
        
        if not valid_ids:
            return []
        
        if len(valid_ids) == len(self.ids):
            return super().read(fields, load)
        
        filtered = self.browse(valid_ids)
        return super(ResPartner, filtered).read(fields, load)
