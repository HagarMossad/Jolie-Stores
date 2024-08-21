# Copyright (c) 2024, Publisher and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	conditions = ' 1=1 '
	if filters.get("item_code"):
		conditions += f" and b.item_code = '{filters.get('item_code')}' "
	if filters.get("warehouse"):
		conditions += f" and b.warehouse = '{filters.get('warehouse')}' "
	sql= f'''
	        select 
			    b.item_code , b.warehouse , b.actual_qty as stock_qty , b.reserved_qty , w.web_item_name ,
	            (b.actual_qty + b.ordered_qty - b.reserved_qty)as qty
			from
			 `tabBin` b
			inner join 
                `tabWebsite Item` w
			where 
                w.item_code = b.item_code
			and 
			    {conditions}
            '''
	data = frappe.db.sql(sql1 , as_dict = 1)
	return data


def get_columns():
	return [
		{
            "label": "Item Code", 
            "fieldname": "item_code", 
            "fieldtype": "Link", 
            "options": "Item"
        },
        {
            "label": "Website Item", 
            "fieldname": "web_item_name", 
            "fieldtype": "Data", 
            # "options": "Website Item"
        },
		{
            "label": "Warehouse", 
            "fieldname": "warehouse", 
            "fieldtype": "Link", 
            "options": "Warehouse"
        },        
		{
            "label": "Stock Qty", 
            "fieldname": "stock_qty", 
            "fieldtype": "Float", 
        },
		{
            "label": "Actual Qty", 
            "fieldname": "qty", 
            "fieldtype": "Float", 
        },		
		{
            "label": "Reserved Qty", 
            "fieldname": "reserved_qty", 
            "fieldtype": "Float", 
        },
		
	]

	
