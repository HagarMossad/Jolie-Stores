import frappe



data = {
    'custom_fields': {
        'Selling Settings': [
            {
                "label": "Default Warehouse",
                "fieldname": "default_warehouse",
                "fieldtype": "Link",
                "insert_after": "territory",
                "options":"Warehouse",
            }
        ],
        'Item': [
            {
                "label": "Offer",
                "fieldname": "offer",
                "fieldtype": "Float",
                "insert_after": "stock_uom",
            }
        ],
    },
}