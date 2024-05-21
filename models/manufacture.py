from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manufacture_related_ids = fields.One2many(
        'custom.related.model',
        'manufacture_id',
        string='Required Specifications'
    )
    sale_order_id = fields.Many2one('sale.order', string='sale order')

