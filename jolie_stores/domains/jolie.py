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
    'Sales Order': [
            {
                "label": "User Details",
                "fieldname": "user_details",
                "fieldtype": "Tab Break",
                "insert_after": "company_address_display",
                "Collapsible" : 1
            },
            {
                "label": "User Name",
                "fieldname": "user_name",
                "fieldtype": "Data",
                "insert_after": "user_details",
            },
            {
                "label": "User Phone",
                "fieldname": "user_phone",
                "fieldtype": "Data",
                "insert_after": "user_name",
            },
            {
                "label": "User Email",
                "fieldname": "user_email",
                "fieldtype": "Data",
                "insert_after": "user_phone",
                "options":"Email",
            },
            {
                "label": "User Address",
                "fieldname": "user_address",
                "fieldtype": "Data",
                "insert_after": "user_email",
            },
            {
                "label": "Notes",
                "fieldname": "notes",
                "fieldtype": "Text",
                "insert_after": "user_address",
            },
            {
                "label": "City",
                "fieldname": "city",
                "fieldtype": "Link",
                "insert_after": "notes",
                "options":"City",
            },
            {
                "label": "Fees",
                "fieldname": "fees",
                "fieldtype": "Float",
                "insert_after": "city",
                "fetch_from":"city.fees", 
                "read_only": 1
            },
            {
                "label": "Date Time",
                "fieldname": "date_time",
                "fieldtype": "Datetime",
                "insert_after": "transaction_date",
            }
        ],
    },
}