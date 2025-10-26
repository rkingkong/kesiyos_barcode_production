from odoo import models, fields, api
from odoo.exceptions import UserError

class BarcodeProductionScanner(models.TransientModel):
    _name = 'barcode.production.scanner'
    _description = 'Scan to Produce'
    
    barcode = fields.Char(string='Scan Barcode', required=True)
    
    @api.onchange('barcode')
    def _onchange_barcode(self):
        if self.barcode:
            # Find BOM with this barcode
            bom = self.env['mrp.bom'].search([
                ('production_barcode', '=', self.barcode)
            ], limit=1)
            
            if bom:
                # Create and complete production
                production = self.env['mrp.production'].create({
                    'product_id': bom.product_id.id,
                    'bom_id': bom.id,
                    'product_qty': 1.0,
                    'product_uom_id': bom.product_uom_id.id,
                })
                
                # Confirm
                production.action_confirm()
                
                # Mark components as consumed
                for move in production.move_raw_ids:
                    move.quantity_done = move.product_uom_qty
                
                # Complete
                production.button_mark_done()
                
                # Show success and clear field
                self.barcode = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': f'Produced 1 batch of {bom.product_id.name}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(f'No BOM found for barcode: {self.barcode}')