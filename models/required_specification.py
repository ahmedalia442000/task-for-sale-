from odoo import fields, models, api

class CustomRelatedModel(models.Model):
    _name = 'custom.related.model'
    _description = 'Custom Related Model'

    name = fields.Selection([
        ('moisture', 'Moisture'),
        ('purity', 'Purity'),
        ('viscosity bf 2%', 'Viscosity bf 2%'),
        ('viscosity av 1%', 'Viscosity av 1%'),
        ('ph', 'PH'),
        ('ds', 'DS'),
        ('salt content', 'Salt Content'), ('density', 'Density'), ('filtrate value', 'Filtrate Value'),
    ], string='Test', sort=False)
    limits = fields.Float(string='Limits')
    batch1 = fields.Float(string='Batch1')
    batch2 = fields.Float(string='Batch2')
    batch3 = fields.Float(string='Batch3')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    manufacture_id = fields.Many2one('mrp.production', string="Manufacture")
    raised_value = fields.Float(
        string='Raised Value',
        compute='_compute_raised_value')

    @api.depends('limits', 'batch1', 'batch2', 'batch3')
    def _compute_raised_value(self):
        for record in self:
            # Here, you can implement the logic for calculating the raised value.
            # For demonstration, let's say it is the sum of limits, batch1, batch2, and batch3.
            record.raised_value = record.limits + record.batch1 + record.batch2 + record.batch3

