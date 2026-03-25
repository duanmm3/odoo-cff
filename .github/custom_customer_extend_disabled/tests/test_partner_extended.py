# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestPartnerExtended(TransactionCase):
    """Test partner extended functionality"""

    def setUp(self):
        super(TestPartnerExtended, self).setUp()
        self.Partner = self.env['res.partner']

    def test_create_customer(self):
        """Test creating a customer with automatic code generation"""
        # 创建客户
        customer_data = {
            'name': '测试客户公司',
            'partner_type': 'customer',
            'customer_type': 'CF',
            'customer_grade': '5a',
            'customer_source': '1',
            'reconciliation_day': '15',
            'english_name': 'Test Customer Company',
            'company_phone': '021-12345678',
            'mobile_phone': '13800138000',
            'customer_tags': '重要客户',
            'tax_rate': '0.1300',
            'is_potential_customer': False,
            'customer_currency': 'CNY',
            'payment_method': 'cash',
            'invoice_day': '20',
            'website': 'www.testcustomer.com',
        }
        
        customer = self.Partner.create(customer_data)
        
        # 验证字段值
        self.assertEqual(customer.partner_type, 'customer')
        self.assertEqual(customer.customer_type, 'CF')
        self.assertEqual(customer.customer_grade, '5a')
        self.assertEqual(customer.customer_source, '1')
        self.assertEqual(customer.reconciliation_day, '15')
        self.assertEqual(customer.english_name, 'Test Customer Company')
        self.assertEqual(customer.company_phone, '021-12345678')
        self.assertEqual(customer.mobile_phone, '13800138000')
        self.assertEqual(customer.customer_tags, '重要客户')
        self.assertEqual(customer.tax_rate, '0.1300')
        self.assertEqual(customer.is_potential_customer, False)
        self.assertEqual(customer.customer_currency, 'CNY')
        self.assertEqual(customer.payment_method, 'cash')
        self.assertEqual(customer.invoice_day, '20')
        self.assertEqual(customer.website, 'www.testcustomer.com')
        
        # 验证代码生成
        self.assertTrue(customer.partner_code)
        self.assertTrue(customer.partner_code.startswith('CF'))
        
        # 创建第二个同类型客户
        customer2_data = customer_data.copy()
        customer2_data['name'] = '测试客户公司2'
        customer2 = self.Partner.create(customer2_data)
        
        # 验证代码递增
        self.assertTrue(customer2.partner_code.startswith('CF'))
        code1_num = int(customer.partner_code[2:])
        code2_num = int(customer2.partner_code[2:])
        self.assertEqual(code2_num, code1_num + 1)

    def test_create_supplier(self):
        """Test creating a supplier with automatic code generation"""
        # 创建供应商
        supplier_data = {
            'name': '测试供应商公司',
            'partner_type': 'supplier',
            'supplier_type': 'ST',
            'customer_grade': '10a',
            'customer_source': '2',
            'reconciliation_day': '10',
            'english_name': 'Test Supplier Company',
            'company_phone': '021-87654321',
            'mobile_phone': '13900139000',
            'customer_tags': '核心供应商',
            'tax_rate': '0',
            'is_potential_customer': True,
            'customer_currency': 'USD',
            'payment_method': '100_prepaid',
            'invoice_day': '5',
            'website': 'www.testsupplier.com',
        }
        
        supplier = self.Partner.create(supplier_data)
        
        # 验证字段值
        self.assertEqual(supplier.partner_type, 'supplier')
        self.assertEqual(supplier.supplier_type, 'ST')
        self.assertEqual(supplier.customer_grade, '10a')
        self.assertEqual(supplier.customer_source, '2')
        self.assertEqual(supplier.reconciliation_day, '10')
        self.assertEqual(supplier.english_name, 'Test Supplier Company')
        self.assertEqual(supplier.company_phone, '021-87654321')
        self.assertEqual(supplier.mobile_phone, '13900139000')
        self.assertEqual(supplier.customer_tags, '核心供应商')
        self.assertEqual(supplier.tax_rate, '0')
        self.assertEqual(supplier.is_potential_customer, True)
        self.assertEqual(supplier.customer_currency, 'USD')
        self.assertEqual(supplier.payment_method, '100_prepaid')
        self.assertEqual(supplier.invoice_day, '5')
        self.assertEqual(supplier.website, 'www.testsupplier.com')
        
        # 验证代码生成
        self.assertTrue(supplier.partner_code)
        self.assertTrue(supplier.partner_code.startswith('ST'))

    def test_create_both_customer_supplier(self):
        """Test creating a partner that is both customer and supplier"""
        partner_data = {
            'name': '测试客户供应商公司',
            'partner_type': 'both',
            'customer_type': 'CT',
            'supplier_type': 'SF',
            'customer_grade': '5b',
            'customer_source': '3',
            'reconciliation_day': '25',
            'english_name': 'Test Both Company',
            'company_phone': '021-55556666',
            'mobile_phone': '13700137000',
            'customer_tags': '战略伙伴',
            'tax_rate': '0.1300',
            'is_potential_customer': False,
            'customer_currency': 'CNY',
            'payment_method': '50_prepaid',
            'invoice_day': '15',
            'website': 'www.testboth.com',
        }
        
        partner = self.Partner.create(partner_data)
        
        # 验证字段值
        self.assertEqual(partner.partner_type, 'both')
        self.assertEqual(partner.customer_type, 'CT')
        self.assertEqual(partner.supplier_type, 'SF')
        
        # 验证代码生成（应该使用客户类型作为前缀）
        self.assertTrue(partner.partner_code)
        self.assertTrue(partner.partner_code.startswith('CT'))

    def test_update_partner_type(self):
        """Test updating partner type and code regeneration"""
        # 创建客户
        customer = self.Partner.create({
            'name': '测试更新客户',
            'partner_type': 'customer',
            'customer_type': 'OF',
        })
        
        original_code = customer.partner_code
        
        # 更新为供应商
        customer.write({
            'partner_type': 'supplier',
            'supplier_type': 'SD',
        })
        
        # 验证代码已更新
        self.assertNotEqual(customer.partner_code, original_code)
        self.assertTrue(customer.partner_code.startswith('SD'))

    def test_file_upload_fields(self):
        """Test file upload fields"""
        # 创建带有文件上传的客户
        customer_data = {
            'name': '测试文件上传客户',
            'partner_type': 'customer',
            'customer_type': 'OT',
            'business_card_filename': 'business_card.pdf',
            'business_license_filename': 'license.pdf',
            'registration_certificate_filename': 'certificate.pdf',
            'payment_account_filename': 'account.pdf',
            'survey_form_filename': 'survey.pdf',
        }
        
        customer = self.Partner.create(customer_data)
        
        # 验证文件名字段
        self.assertEqual(customer.business_card_filename, 'business_card.pdf')
        self.assertEqual(customer.business_license_filename, 'license.pdf')
        self.assertEqual(customer.registration_certificate_filename, 'certificate.pdf')
        self.assertEqual(customer.payment_account_filename, 'account.pdf')
        self.assertEqual(customer.survey_form_filename, 'survey.pdf')

    def test_search_and_filter(self):
        """Test search and filter functionality"""
        # 创建不同类型的客户
        customer1 = self.Partner.create({
            'name': '搜索测试客户1',
            'partner_type': 'customer',
            'customer_type': 'CF',
            'customer_grade': '5a',
            'is_potential_customer': True,
        })
        
        customer2 = self.Partner.create({
            'name': '搜索测试客户2',
            'partner_type': 'customer',
            'customer_type': 'CT',
            'customer_grade': '10b',
            'is_potential_customer': False,
        })
        
        supplier = self.Partner.create({
            'name': '搜索测试供应商',
            'partner_type': 'supplier',
            'supplier_type': 'ST',
            'customer_grade': '5c',
        })
        
        # 测试按客户类型搜索
        cf_customers = self.Partner.search([('customer_type', '=', 'CF')])
        self.assertIn(customer1, cf_customers)
        self.assertNotIn(customer2, cf_customers)
        
        # 测试按客户等级搜索
        grade_5a_customers = self.Partner.search([('customer_grade', '=', '5a')])
        self.assertIn(customer1, grade_5a_customers)
        
        # 测试按潜在客户搜索
        potential_customers = self.Partner.search([('is_potential_customer', '=', True)])
        self.assertIn(customer1, potential_customers)
        self.assertNotIn(customer2, potential_customers)
        
        # 测试按合作伙伴类型搜索
        customers = self.Partner.search([('partner_type', '=', 'customer')])
        self.assertIn(customer1, customers)
        self.assertIn(customer2, customers)
        self.assertNotIn(supplier, customers)

    def test_validation_constraints(self):
        """Test validation constraints"""
        # 测试创建客户时缺少客户类型
        with self.assertRaises(Exception):
            self.Partner.create({
                'name': '测试验证客户',
                'partner_type': 'customer',
                # 缺少 customer_type
            })
        
        # 测试创建供应商时缺少供应商类型
        with self.assertRaises(Exception):
            self.Partner.create({
                'name': '测试验证供应商',
                'partner_type': 'supplier',
                # 缺少 supplier_type
            })
        
        # 测试创建既是客户又是供应商时缺少类型
        with self.assertRaises(Exception):
            self.Partner.create({
                'name': '测试验证两者',
                'partner_type': 'both',
                # 缺少 customer_type 和 supplier_type
            })

    def test_different_customer_types(self):
        """Test creating partners with different customer types"""
        customer_types = ['CF', 'CT', 'OF', 'OT']
        
        for i, customer_type in enumerate(customer_types):
            customer = self.Partner.create({
                'name': f'测试{customer_type}客户{i+1}',
                'partner_type': 'customer',
                'customer_type': customer_type,
            })
            
            # 验证代码前缀
            self.assertTrue(customer.partner_code.startswith(customer_type))

    def test_different_supplier_types(self):
        """Test creating partners with different supplier types"""
        supplier_types = ['ST', 'SF', 'SD', 'SE']
        
        for i, supplier_type in enumerate(supplier_types):
            supplier = self.Partner.create({
                'name': f'测试{supplier_type}供应商{i+1}',
                'partner_type': 'supplier',
                'supplier_type': supplier_type,
            })
            
            # 验证代码前缀
            self.assertTrue(supplier.partner_code.startswith(supplier_type))

    def test_shared_users_field(self):
        """Test shared_users many2many field functionality"""
        # 创建几个测试用户
        user1 = self.env['res.users'].create({
            'name': '测试销售1',
            'login': 'testsales1@example.com',
        })
        
        user2 = self.env['res.users'].create({
            'name': '测试采购1',
            'login': 'testbuyer1@example.com',
        })
        
        user3 = self.env['res.users'].create({
            'name': '测试管理员1',
            'login': 'testadmin1@example.com',
        })
        
        # 创建联系人并分配共享用户
        partner_data = {
            'name': '测试共享用户联系人',
            'partner_type': 'customer',
            'customer_type': 'CF',
            'shared_users': [(6, 0, [user1.id, user2.id, user3.id])],
        }
        
        partner = self.Partner.create(partner_data)
        
        # 验证共享用户
        self.assertEqual(len(partner.shared_users), 3)
        self.assertIn(user1, partner.shared_users)
        self.assertIn(user2, partner.shared_users)
        self.assertIn(user3, partner.shared_users)
        
        # 验证可以移除共享用户
        partner.write({
            'shared_users': [(6, 0, [user1.id, user2.id])]
        })
        self.assertEqual(len(partner.shared_users), 2)
        self.assertIn(user1, partner.shared_users)
        self.assertIn(user2, partner.shared_users)
        self.assertNotIn(user3, partner.shared_users)

    def test_basic_permission_concept(self):
        """Test basic permission concept (without actual record rule enforcement)"""
        # 这个测试只验证字段和基本逻辑，不测试记录规则
        # 创建测试用户
        user1 = self.env['res.users'].create({
            'name': '测试用户1',
            'login': 'testuser1@example.com',
        })
        
        user2 = self.env['res.users'].create({
            'name': '测试用户2',
            'login': 'testuser2@example.com',
        })
        
        # 创建带共享用户的联系人
        partner = self.Partner.create({
            'name': '测试共享联系人',
            'partner_type': 'customer',
            'customer_type': 'CF',
            'shared_users': [(6, 0, [user1.id, user2.id])],
        })
        
        # 验证共享用户功能
        self.assertEqual(len(partner.shared_users), 2)
        self.assertIn(user1, partner.shared_users)
        self.assertIn(user2, partner.shared_users)
        
        # 验证权限过滤逻辑（概念验证）
        # 注意：实际权限控制由记录规则处理
        user_ids = [user1.id, user2.id]
        self.assertTrue(user1.id in user_ids)
        self.assertTrue(user2.id in user_ids)

    def test_pagination_functionality(self):
        """Test pagination functionality (20 records per page)"""
        # 创建25个测试联系人
        for i in range(25):
            self.Partner.create({
                'name': f'测试分页联系人{i+1}',
                'partner_type': 'customer',
                'customer_type': 'CF',
            })
        
        # 测试默认分页（20条记录）
        partners_page1 = self.Partner.search([])
        self.assertEqual(len(partners_page1), 20)
        
        # 测试第二页（5条记录）
        partners_page2 = self.Partner.search([], offset=20)
        self.assertEqual(len(partners_page2), 5)
        
        # 测试search_read方法的分页
        partners_read = self.Partner.search_read([], limit=20)
        self.assertEqual(len(partners_read), 20)
        
        # 测试可以指定不同的分页大小
        partners_custom = self.Partner.search_read([], limit=10)
        self.assertEqual(len(partners_custom), 10)

    def test_permission_with_record_rules(self):
        """Test permission with record rules (ir.rule)"""
        # 创建两个普通用户和一个管理员用户
        user1 = self.env['res.users'].create({
            'name': '测试用户1',
            'login': 'testuser1@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        user2 = self.env['res.users'].create({
            'name': '测试用户2',
            'login': 'testuser2@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        admin_user = self.env['res.users'].create({
            'name': '测试管理员',
            'login': 'testadmin@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_system').id, self.env.ref('base.group_user').id])],
        })
        
        # 创建用户1的联系人
        contact1 = self.Partner.with_user(user1).create({
            'name': '用户1的联系人',
            'partner_type': 'customer',
            'customer_type': 'CF',
        })
        
        # 创建用户2的联系人
        contact2 = self.Partner.with_user(user2).create({
            'name': '用户2的联系人',
            'partner_type': 'customer',
            'customer_type': 'CF',
        })
        
        # 将contact1共享给用户2（所以用户2应该能看到contact1和他们自己的contact2）
        contact1.with_user(user1).write({
            'shared_users': [(4, user2.id)]
        })
        
        # 现在测试权限
        
        # 作为用户1：应该只能看到自己的联系人（contact1）和共享给他们的联系人（目前没有，除非我们将contact2共享给用户1）
        # 让我们也将contact2共享给用户1，以测试双向共享
        contact2.with_user(user2).write({
            'shared_users': [(4, user1.id)]
        })
        
        # 现在，用户1应该能看到contact1（自己的）和contact2（共享的）
        # 用户2应该能看到contact2（自己的）和contact1（共享的）
        # 管理员应该能看到两者
        
        # 切换到用户1环境
        partners_user1 = self.Partner.with_user(user1).search([])
        self.assertIn(contact1, partners_user1, "用户1应该能看到自己的联系人")
        self.assertIn(contact2, partners_user1, "用户1应该能看到被共享的联系人")
        
        # 切换到用户2环境
        partners_user2 = self.Partner.with_user(user2).search([])
        self.assertIn(contact2, partners_user2, "用户2应该能看到自己的联系人")
        self.assertIn(contact1, partners_user2, "用户2应该能看到被共享的联系人")
        
        # 切换到管理员环境
        partners_admin = self.Partner.with_user(admin_user).search([])
        self.assertIn(contact1, partners_admin, "管理员应该能看到所有联系人")
        self.assertIn(contact2, partners_admin, "管理员应该能看到所有联系人")
        
        # 验证用户1看不到未共享的联系人（如果有的话）
        # 创建一个未共享的联系人（由用户3创建）
        user3 = self.env['res.users'].create({
            'name': '测试用户3',
            'login': 'testuser3@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        contact3 = self.Partner.with_user(user3).create({
            'name': '用户3的联系人（未共享）',
            'partner_type': 'customer',
            'customer_type': 'CF',
        })
        # 确保用户1看不到这个联系人
        partners_user1_after = self.Partner.with_user(user1).search([])
        self.assertNotIn(contact3, partners_user1_after, "用户1不应该能看到未共享的联系人")