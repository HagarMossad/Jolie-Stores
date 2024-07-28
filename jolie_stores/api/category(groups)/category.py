import frappe 
from frappe import _
from jolie_stores.api.products.item import products , get_path
# base_url = frappe.utils.get_url() 
# port = "50" 

@frappe.whitelist(allow_guest = True)
def get_all_category(limit =None):
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    try :
        condition = ""  
        if limit : 
            condition = f"limit {limit}" 
        sql = f'''
                SELECT 
                    name as category_id , item_group_name as category_name , image 
                FROM
                    `tabItem Group`
                {condition}
                '''
        groups = frappe.db.sql(sql , as_dict = 1) 
        for group in groups:
            if group["image"]:
                group["image"] = get_path(group["image"])
        return groups
    except :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "An error occurred while fetching categories"
        return

@frappe.whitelist(allow_guest = True)
def get_category_detailss(category):
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    
    sql = f'''
            SELECT 
                i.name as product_id, i.website_image ,
                (SELECT price_list_rate FROM `tabItem Price` WHERE item_code =i.item_code order by creation desc limit 1 ) as price ,
                (g.name) as category_id , g.item_group_name , g.image
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
    dict = {}
    products = frappe.db.sql(sql , as_dict = 1)
    if not products :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "No category with the same name"
        return
    list =[]
    for product in products :
        dict_list = {}
        dict_list["product_id"] = product["product_id"]
        if product["website_image"] :
            dict_list["website_image"] = get_path(product["website_image"])
        else :
            dict_list["website_image"] = product["website_image"]

        dict_list["price"] = product["price"]
        dict_list["category_id"] = product["category_id"]
        dict_list["category_name"] = product["item_group_name"]
        list.append(dict_list)   
    dict["products"] = list     

    dict["category"] = {
        "category_id" : products[0]["category_id"] ,
        "category_name" :  products[0]["item_group_name"] ,
        "image" : products[0]["image"] 
    }
    return dict




@frappe.whitelist(allow_guest = True)
def get_category_details(category = None):
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    if not category :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Define category"
        return
    all_products = products(category = category)
    dict = {}
    category_obj = {}
    dict["products"] = []
    if all_products :
        dict["products"] = all_products
    sql = F'''
            SELECT 
                name as category_id, item_group_name as category_name
            FROM 
                `tabItem Group`
            WHERE
                name = '{category}' '''
    category_details = frappe.db.sql(sql , as_dict =1)
    if category_details :
        category_obj["category_id"] = category_details[0]["category_id"]
        category_obj["category_name"] = category_details[0]["category_name"]
        dict["category"] = category_obj
        return dict
    else :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Not Exist"
        return

