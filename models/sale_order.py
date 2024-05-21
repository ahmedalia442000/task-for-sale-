from odoo import fields, models, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_related_ids = fields.One2many(
        'custom.related.model',
        'order_id',
        string='Required Specification'

    )
    manufacturing_order_count = fields.Integer(string="Manufacturing Orders",
                                               compute='_compute_manufacturing_order_count')
    grade = fields.Text(string="Grade")
    req_bef = fields.Date(string="Req.Before")
    po = fields.Text(string="PO No.")

    # @api.onchange('custom_related_ids')
    # def _onchange_custom_related_ids(self):
    #     """Synchronize manufacture_related_ids in mrp.production with custom_related_ids in sale.order."""
    #     for rec in self:
    #         # البحث عن mrp.production المرتبطة بالسجل الحالي
    #         manufacturing_order = self.env['mrp.production'].search([
    #             ('sale_order_id', '=', rec.id)
    #         ], limit=1)
    #
    #         # تأكد من العثور على mrp.production
    #         if manufacturing_order:
    #             # استخدام قاموس لتخزين البيانات الجديدة لـ manufacture_related_ids
    #             manufacture_related_data = {}
    #
    #             # تكرار custom_related_ids في sale.order
    #             for related_line in rec.custom_related_ids:
    #                 # البحث عن السطر المطابق في manufacture_related_ids
    #                 corresponding_line = manufacturing_order.manufacture_related_ids.filtered(
    #                     lambda l: l.name == related_line.name
    #                 )
    #
    #                 if corresponding_line:
    #                     # تحديث الحقول في السطر المطابق باستخدام write
    #                     corresponding_line.write({
    #                         'name': related_line.name,
    #
    #                         'limits': related_line.limits,
    #                         'batch1': related_line.batch1,
    #                         'batch2': related_line.batch2,
    #                         'batch3': related_line.batch3,
    #                     })
    #
    #                 else:
    #                     # إذا لم يتم العثور على السطر، قم بإضافة سطر جديد (إذا لزم الأمر)
    #                     new_line = manufacturing_order.env['custom.related.model'].create({
    #                         'name': related_line.name,
    #                         'limits': related_line.limits,
    #                         'batch1': related_line.batch1,
    #                         'batch2': related_line.batch2,
    #                         'batch3': related_line.batch3,
    #                         'manufacture_id': manufacturing_order.id,
    #                     })

    def write(self, vals):
        # قم بحفظ الحالة الحالية قبل التحديث
        result = super(SaleOrder, self).write(vals)

        # تحقق مما إذا كان هناك تغيير في custom_related_ids
        if 'custom_related_ids' in vals:
            # إذا كان هناك تغيير، قم بمزامنة manufacture_related_ids
            for rec in self:
                # البحث عن mrp.production المرتبطة بالسجل الحالي
                manufacturing_order = self.env['mrp.production'].search([
                    ('sale_order_id', '=', rec.id)
                ])
                # إذا تم العثور على mrp.production
                if manufacturing_order:
                    for mo_order in manufacturing_order :
                        for mo in mo_order.manufacture_related_ids :
                            mo.sudo().unlink()
                    # إعداد قائمة التحديث
                    manufacture_related_values = []
                    for line in rec.custom_related_ids:

                        val = {

                            'name': line.name,
                            'limits': line.limits,
                            'batch1': line.batch1,
                            'batch2': line.batch2,
                            'batch3': line.batch3,
                        }
                        manufacture_related_values.append((0, 0, val))

                    # تحديث manufacture_related_ids في mrp.production
                    manufacturing_order.update({'manufacture_related_ids': manufacture_related_values})

        # إرجاع نتيجة الأسلوب الأصلي
        return result



    @api.depends('order_line.product_id')
    def _compute_manufacturing_order_count(self):
        for order in self:
            manufacturing_order_count = 0
            # for line in order.order_line:
            manufacturing_order_count = self.env['mrp.production'].search_count(
                [('sale_order_id', '=', order.id)])
            order.manufacturing_order_count = manufacturing_order_count
            print(';;;;;;;;;;', order.manufacturing_order_count)

    def action_view_manufacturing_orders(self):
        return {
            'name': _('manufactures'),
            'view_mode': 'list,form',
            'res_model': 'mrp.production',
            'target': 'current',
            'domain': [('sale_order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }




    def action_confirm(self):
        # Call the original action_confirm method
        super(SaleOrder, self).action_confirm()

        # Create manufacturing orders for each product in the sale order lines
        for order in self:
            for line in order.order_line:
                # Create a manufacturing order
                production_order = self.env['mrp.production'].create({
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom_id': line.product_uom.id,  # Set product UOM
                    'sale_order_id' : line.order_id.id

                    # Add other relevant fields here
                })

                # Pass values from sale order's custom_related_ids to manufacturing order's manufacture_related_ids
                manufacture_related_values = []
                for custom_related in order.custom_related_ids:
                    manufacture_related_values.append((0, 0, {
                        'name': custom_related.name,
                        'limits': custom_related.limits,
                        'batch1': custom_related.batch1,
                        'batch2': custom_related.batch2,
                        'batch3': custom_related.batch3,
                    }))
                production_order.manufacture_related_ids = manufacture_related_values

                # Confirm the manufacturing order
                production_order.action_confirm()


