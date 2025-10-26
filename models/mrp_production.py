from odoo import models, fields, api
import random
import string

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    production_barcode = fields.Char(
        string='Production Barcode',
        help='Scan this to produce 1 batch'
    )
    
    @api.model
    def create(self, vals):
        # Auto-generate barcode if not provided
        if 'production_barcode' not in vals or not vals['production_barcode']:
            # Generate unique code like "PROD-ABC123"
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            vals['production_barcode'] = f"PROD-{code}"
        return super().create(vals)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    @api.model
    def create_production_from_barcode(self, barcode):
        """Create and complete production from barcode scan"""
        bom = self.env['mrp.bom'].search([
            ('production_barcode', '=', barcode)
        ], limit=1)
        
        if not bom:
            return {'error': 'No BOM found for this barcode'}
        
        # Create production order
        production = self.create({
            'product_id': bom.product_id.id,
            'bom_id': bom.id,
            'product_qty': 1.0,
            'product_uom_id': bom.product_uom_id.id,
        })
        
        # Confirm production
        production.action_confirm()
        
        # Set consumed quantities
        for move in production.move_raw_ids:
            move.quantity_done = move.product_uom_qty
        
        # Complete production
        production.button_mark_done()
        
        return {
            'success': True,
            'production_id': production.id,
            'message': f'Produced 1 batch of {bom.product_id.name}'
        }