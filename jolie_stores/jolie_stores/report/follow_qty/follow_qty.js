// Copyright (c) 2024, Publisher and contributors
// For license information, please see license.txt

frappe.query_reports["Follow Qty"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		
	]
};
