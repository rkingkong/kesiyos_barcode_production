{
    'name': 'Kesiyos Barcode Production',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Scan barcode to complete batch production',
    'depends': ['mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_views.xml',
        'wizard/barcode_scanner.xml',
    ],
    'installable': True,
    'application': False,
}