from odoo import models, fields, api
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    production_barcode = fields.Char(
        string='Production Barcode',
        help='Scan this to produce 1 batch'
    )
    
    @api.model
    def create(self, vals):
        """Auto-generate barcode if not provided"""
        if not vals.get('production_barcode'):
            product_name = vals.get('code', 'BATCH')
            clean_name = ''.join(c for c in product_name if c.isalnum())[:4].upper()
            sequence = self.search_count([]) + 1
            vals['production_barcode'] = f"{clean_name}-{sequence:03d}"
        return super().create(vals)

    @api.model
    def process_production_barcode(self, barcode):
        """Process barcode scan and create production"""
        bom = self.search([('production_barcode', '=', barcode)], limit=1)
        
        if not bom:
            return {'success': False, 'message': f'No BOM found for barcode: {barcode}'}
        
        # Create production order
        production = self.env['mrp.production'].create({
            'product_id': bom.product_id.id,
            'bom_id': bom.id,
            'product_qty': 1.0,
            'product_uom_id': bom.product_uom_id.id,
        })
        
        # Confirm and complete
        production.action_confirm()
        
        # Auto-consume materials
        for move in production.move_raw_ids:
            move.quantity_done = move.product_uom_qty
        
        # Mark as done
        production.button_mark_done()
        
        return {
            'success': True,
            'message': f'✓ Produced 1 batch of {bom.product_id.name}'
        }