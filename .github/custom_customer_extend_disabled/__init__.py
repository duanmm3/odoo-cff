from . import models


def post_init_hook(env):
    """
    设置默认 partner_type 和同步历史共享数据
    """
    # 设置默认 partner_type
    env.cr.execute("""
        UPDATE res_partner
        SET partner_type = 'other'
        WHERE partner_type IS NULL
    """)

    # 同步历史共享数据：如果联系人有 shared_users 记录，但表中字段为空，把创建者加入共享
    env.cr.execute("""
        UPDATE res_partner p
        SET shared_users = array_append(COALESCE(shared_users, ARRAY[]::integer[]), p.create_uid)
        WHERE p.create_uid IS NOT NULL
        AND p.id IN (
            SELECT partner_id FROM partner_shared_users_rel
        )
        AND NOT (p.shared_users && ARRAY[p.create_uid])
    """)

    env.cr.commit()
    print("=== 模块已加载，历史共享数据已同步 ===")


def uninstall_hook(env):
    pass
