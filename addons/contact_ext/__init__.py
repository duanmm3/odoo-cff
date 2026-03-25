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
 


def uninstall_hook(env):
    pass
