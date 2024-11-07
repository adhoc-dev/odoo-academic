##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _set_deferred_end_date_from_template(self):
        self.ensure_one()
        if (not self.sale_order_template_id or self.sale_order_template_id.is_unlimited) and self.plan_id and not self.plan_id.is_unlimited:
            self.write({'end_date': self.start_date + self.plan_id.duration - relativedelta(days=1)})
        else:
            super()._set_deferred_end_date_from_template()

    @api.constrains('sale_order_template_id', 'plan_id')
    def _check_period(self):
        for rec in self:
            if rec.sale_order_template_id and not rec.sale_order_template_id.is_unlimited and rec.plan_id and not rec.plan_id.is_unlimited:
                raise UserError(_('There cannot be a sale order template and a recurring plan both with a defined period.'))

    def _get_auto_invoice_grouping_keys(self):
        grouping_keys = super()._get_auto_invoice_grouping_keys() + ['partner_id', 'partner_invoice_id', 'payment_term_id']
        grouping_keys = list(set(grouping_keys))
        return grouping_keys

    def action_update_prices(self):
        if self._context.get('action_update_subscription_prices'):
            lines = self.order_line.filtered(
                lambda line: not bool(
                    self.env['sale.subscription.pricing']._get_first_suitable_recurring_pricing(
                        line.product_id, line.plan_id, line.order_id.pricelist_id
                    )
                )
            )
            lines_price_unit = {line: line.price_unit for line in lines}
            super().action_update_prices()
            for line, original_price in lines_price_unit.items():
                if line.exists():
                    line.price_unit = original_price
        else:
            super().action_update_prices()
