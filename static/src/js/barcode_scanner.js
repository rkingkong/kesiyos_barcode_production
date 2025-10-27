odoo.define('kesiyos_barcode_production.scanner', function(require) {
    'use strict';
    
    var core = require('web.core');
    var Widget = require('web.Widget');
    
    var Scanner = Widget.extend({
        template: 'kesiyos_barcode_scanner',
        
        start: function() {
            var self = this;
            this.$('input').focus();
            this.$('input').on('keypress', function(e) {
                if (e.which === 13) { // Enter key
                    self.processBarcode($(this).val());
                    $(this).val('');
                }
            });
        },
        
        processBarcode: function(barcode) {
            var self = this;
            this._rpc({
                model: 'mrp.bom',
                method: 'process_production_barcode',
                args: [barcode],
            }).then(function(result) {
                if (result.success) {
                    self.do_notify('Success', result.message);
                } else {
                    self.do_warn('Error', result.message);
                }
            });
        },
    });
    
    core.action_registry.add('kesiyos_scanner', Scanner);
    return Scanner;
});