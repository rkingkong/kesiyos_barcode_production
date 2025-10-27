{
    'name': 'Kesiyos Barcode Production',
    'version': '17.0.1.0.0',
    'depends': ['mrp', 'stock', 'barcodes'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_views.xml',
        'wizard/barcode_scanner.xml',
        'reports/bom_report.xml',
    ],
    'installable': True,
}