##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

def post_init_hook(env):
    templates = env['mail.template'].search([('model_id.model', '=', 'sale.order')])
    templates.use_default_to = True
