import frappe 
from frappe import _

@frappe.whitelist(allow_guest = True)
def get_all_category():
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    try :
        base_url = frappe.utils.get_url()    
        sql = f'''
                SELECT 
                    name as category_id , item_group_name as category_name , image 
                FROM
                    `tabItem Group`
                '''
        groups = frappe.db.sql(sql , as_dict = 1) 
        for group in groups:
            if group["image"]:
                group["image"] = f"{base_url}"+group["image"]
        return groups
    except :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "An error occurred while fetching categories"
        return

@frappe.whitelist(allow_guest = True)
def get_category_details(category):
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    sql = f'''
            SELECT 
                i.name as product_id, i.website_image , (SELECT price_list_rate FROM `tabItem Price` WHERE item_code =i.item_code order by creation desc limit 1 ) as price ,
                (g.name) as category_name, g.item_group_name
            FROM
                `tabWebsite Item` i
            INNER JOIN 
                `tabItem Group` g
            ON 
                i.item_group = g.name
            WHERE
                i.item_group = '{category}'
                and
                (i.has_variants = 1
                or 
                i.variant_of is not null  )
            '''
    products = frappe.db.sql(sql , as_dict = 1) 
    return products


