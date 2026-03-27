# 发票审批流程优化 - 2026年3月27日

## 业务需求

普通用户（如Susan）创建发票/账单时：
- 金额超过5000元 → 状态变为"待审批"
- 金额不超过5000元 → 直接过账
- 待审批状态：不能确认、不能支付
- 审批通过后：可以确认过账、可以支付

## 修改内容

### 1. 发票模型 (account_move.py)

**字段变更：**
- `approval_state`: 状态值从 `no/pending/approved/rejected` 改为 `draft/pending/approved/rejected`
- 默认值从 `no` 改为 `draft`

**逻辑变更：**
- `_compute_need_approval`: 从配置参数 `approval_flow.invoice_limit` 读取金额限制，默认5000
- `_get_invoice_limit()`: 获取配置参数方法
- `action_post()`: 
  - 待审批状态阻止确认
  - 金额超限时自动创建审批请求
- `_create_approval_request()`: 自动创建审批请求并发送通知
- `action_register_payment()`: 待审批状态阻止支付
- `action_approve_invoice()`: 管理员审批通过按钮

### 2. 审批请求模型 (approval_request.py)

**逻辑变更：**
- `_execute_approved_action()`: 使用 `sudo()` 更新发票审批状态

### 3. 视图 (account_move_approval.xml)

- 列表页：显示审批状态badge（待审批=黄色）
- 表单页：
  - 移除"提交审批"按钮
  - 移除"查看审批"按钮
  - 管理员在待审批状态可见"审批通过"按钮

### 4. 付款模型 (account_payment.py)

- 简化：移除金额检查逻辑
- 审批通过后自动继承发票审批状态

### 5. 配置

- 使用 `ir.config_parameter` 存储金额限制
- 参数key: `approval_flow.invoice_limit`
- 默认值: 5000

## 业务流程

1. **用户创建发票（草稿）** → 输入金额
2. **点击确认**：
   - 金额>5000 → 自动创建审批请求 → 状态变为"待审批" → 提示用户等待审批
   - 金额≤5000 → 直接过账
3. **待审批状态**：用户不能确认、不能支付
4. **管理员审批**：
   - 进入审批单列表
   - 点击"审批通过"
   - 发票状态变为"已批准"
5. **用户支付**：审批通过后可以正常支付

## 升级命令

```bash
python odoo-bin -d app --db_host=127.0.0.1 --db_port=5432 --db_user=odoo --db_password=odoo -u approval_flow --stop-after-init
```