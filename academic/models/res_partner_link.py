##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):

    _name = 'res.partner.link'
    _description = 'res.partner.link'

    student_id = fields.Many2one('res.partner', 'Student or Family', required=True, ondelete='cascade')
    # student_id = fields.Many2one('res.partner', 'Student', ondelete='cascade')
    # family_id = fields.Many2one('res.partner', 'Family', ondelete='cascade')
    relationship_id = fields.Many2one('res.partner.relationship', required=True, ondelete='restrict')
    role_ids = fields.Many2many('res.partner.role', string='Roles')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict')
    note = fields.Text(string="Notas")

    # @api.constrains('student_id', 'family_id')
    # def _check_student_or_family(self):
    #     recs = self.filtered(lambda x: not x.student_id and not x.family_id)
    #     if recs:
    #         raise UserError('Los contactos y roles deben estar vinculados a una famila o a un estudiante')

    _sql_constraints = [
        ('link_unique',
         'unique(student_id, partner_id)',
         'El contacto debe ser agregado por unica vez en cada familia o estudiante')]

    def write(self, vals):
        if 'role_ids' in vals and self.student_id.partner_type == 'family':
            self._check_active_sale_orders(vals.get('role_ids', []))
        return super().write(vals)

    def _check_active_sale_orders(self, role_ids):
        """
        Si se borra el rol de responsable de pago en el contacto, se verifica
        que el mismo no tenga órdenes de venta activas.
        """
        roles_to_remove = set(self.role_ids.ids) - set(role_ids[0][2])
        if self.env.ref('academic.paying_role').id in roles_to_remove:
            orders = self.env['sale.order'].search([
                ('partner_invoice_id', '=', self.partner_id.id),
                ('state', 'in', ['draft', 'sent']),
                ('partner_id', 'in', self.student_id.student_ids.ids),
            ])
            if orders:
                msg = "Hay órdenes de venta activas que tienen el responsable de pago %s en la dirección de facturación." % self.partner_id.name
                msg += "\nLas siguientes órdenes tienen esa condición:\n\n - %s" % '\n - '.join(orders.mapped('name'))
                raise ValidationError(msg)
