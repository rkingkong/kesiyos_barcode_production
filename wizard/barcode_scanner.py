from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BarcodeProductionScanner(models.TransientModel):
    _name = 'barcode.production.scanner'
    _description = 'Barcode Production Scanner'
    
    barcode = fields.Char(
        string='Scan Barcode',
        required=True,
        help='Scan or enter the production barcode here'
    )
    
    result_message = fields.Html(
        string='Result',
        readonly=True,
    )
    
    @api.onchange('barcode')
    def _onchange_barcode(self):
        """Process barcode immediately when scanned"""
        if self.barcode and len(self.barcode) > 3:  # Minimum barcode length
            # Process the barcode
            result = self.env['mrp.bom'].process_production_barcode(self.barcode)
            
            if result['success']:
                # Show success notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Production Complete!' if result['type'] == 'success' else 'Warning',
                        'message': result['message'],
                        'type': result['type'],
                        'sticky': False,
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }
            else:
                # Show error
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'message': result['message'],
                        'type': 'danger',
                        'sticky': True,
                    }
                }
    
    def action_process_barcode(self):
        """Manual button to process barcode"""
        self.ensure_one()
        
        if not self.barcode:
            raise UserError('Please scan or enter a barcode first.')
        
        result = self.env['mrp.bom'].process_production_barcode(self.barcode)
        
        if result['success']:
            # Create a notification and close wizard
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!' if result['type'] == 'success' else 'Warning',
                    'message': result['message'],
                    'type': result['type'],
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        else:
            raise UserError(result['message'])