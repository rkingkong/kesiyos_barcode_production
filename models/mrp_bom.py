from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    production_barcode = fields.Char(
        string='Production Barcode',
        help='Scan this barcode to automatically produce 1 batch',
        copy=False,
        index=True,
    )
    
    @api.model
    def create(self, vals):
        """Auto-generate barcode if not provided"""
        if not vals.get('production_barcode'):
            # Get product reference or name
            if vals.get('product_tmpl_id'):
                product = self.env['product.template'].browse(vals['product_tmpl_id'])
                base_name = product.default_code or product.name or 'BATCH'
            elif vals.get('code'):
                base_name = vals['code']
            else:
                base_name = 'BATCH'
            
            # Clean and format
            clean_name = ''.join(c for c in base_name if c.isalnum())[:8].upper()
            sequence = self.search_count([]) + 1
            vals['production_barcode'] = f"{clean_name}-{sequence:04d}"
            
        return super().create(vals)
    
    @api.model
    def process_production_barcode(self, barcode):
        """
        Process a scanned barcode and create/complete a production order
        Called from the barcode scanner interface
        """
        try:
            # Find BOM with this barcode
            bom = self.search([('production_barcode', '=', barcode)], limit=1)
            
            if not bom:
                _logger.warning(f'No BOM found for barcode: {barcode}')
                return {
                    'success': False,
                    'message': f'❌ No recipe found for barcode: {barcode}',
                    'type': 'danger',
                }
            
            # Check if product is active and has inventory
            if not bom.product_id.active:
                return {
                    'success': False,
                    'message': f'❌ Product {bom.product_id.name} is archived',
                    'type': 'warning',
                }
            
            # Create production order
            production = self.env['mrp.production'].create({
                'product_id': bom.product_id.id,
                'bom_id': bom.id,
                'product_qty': 1.0,
                'product_uom_id': bom.product_uom_id.id,
                'origin': f'Barcode Scan: {barcode}',
            })
            
            _logger.info(f'Created production order {production.name} for {bom.product_id.name}')
            
            # Confirm the production
            production.action_confirm()
            
            # Check material availability
            missing_materials = []
            for move in production.move_raw_ids:
                if move.product_uom_qty > move.product_id.qty_available:
                    missing_materials.append({
                        'product': move.product_id.name,
                        'needed': move.product_uom_qty,
                        'available': move.product_id.qty_available,
                    })
            
            if missing_materials:
                warning_msg = f'⚠️  Production {production.name} created but materials may be insufficient:\n'
                for mat in missing_materials:
                    warning_msg += f"  • {mat['product']}: need {mat['needed']}, have {mat['available']}\n"
                
                return {
                    'success': True,
                    'message': warning_msg,
                    'type': 'warning',
                    'production_id': production.id,
                    'production_name': production.name,
                }
            
            # Auto-consume materials (set quantity_done = planned quantity)
            for move in production.move_raw_ids:
                move.quantity_done = move.product_uom_qty
            
            # Complete the production
            production.button_mark_done()
            
            _logger.info(f'Completed production {production.name} - produced {production.product_qty} {production.product_uom_id.name} of {production.product_id.name}')
            
            return {
                'success': True,
                'message': f'✅ Produced 1 batch of {bom.product_id.name}\n📦 Production: {production.name}',
                'type': 'success',
                'production_id': production.id,
                'production_name': production.name,
            }
            
        except Exception as e:
            _logger.error(f'Error processing barcode {barcode}: {str(e)}', exc_info=True)
            return {
                'success': False,
                'message': f'❌ Error: {str(e)}',
                'type': 'danger',
            }