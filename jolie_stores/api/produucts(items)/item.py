import frappe 

@frappe.whitelist(allow_guest=True)
def validate_carts(carts):
    if not carts:
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "No carts provided"
        return

    flag = True
    for cart in carts:
        #check id exist or not 
        if 'id' not in cart or 'qty' not in cart or 'price' not in cart: 
            frappe.local.response['http_status_code'] = 404 
            frappe.local.response['data'] = "Invalid cart data"
            return
        sql = f'''
                SELECT 
                    item_code 
                FROM
                    `tabWebsite Item`
                WHERE
                    name ='{cart["id"]}'
            '''
        item_code = frappe.db.sql(sql, as_dict=1)
        if item_code :
            price = get_item_price(item_code[0]["item_code"], get_price_list())
            item_qty = get_qty_bin(item_code[0]["item_code"] , get_warehouse())
            if cart["price"] == price and cart["qty"]  <= item_qty:
                flag = True
            else :
                flag = False
                cart["price"] = price
                cart ["qty"] = item_qty     
        else :
            frappe.local.response['http_status_code'] = 404
            frappe.local.response['data'] = "Invalid ID cart"
            return
    if flag == True :
        return []
    else :
        return carts
    
@frappe.whitelist(allow_guest=True) 
def create_order(carts , user):
    if len(validate_carts(carts)) > 0:
        return carts
    else:
        sales_order = frappe.new_doc("Sales Order")
        

def get_warehouse():
    selling_settings = frappe.get_single("Selling Settings")
    return selling_settings.default_warehouse

def get_price_list():
    selling_settings = frappe.get_single("Selling Settings")
    return selling_settings.selling_price_list
  

@frappe.whitelist(allow_guest = True)
##################################offer
def get_product_details(item):
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    try:
        website_item = frappe.get_doc("Website Item" ,item)        
        names = []
        if website_item.has_variants:
            sql = '''
                SELECT 
                    name as product_id , item_code ,slideshow
                FROM
                    `tabWebsite Item`
                WHERE
                    variant_of = %s
            '''
            products = frappe.db.sql(sql, (website_item.item_code,), as_dict=1)
            for product in products:
                sql_website = f"""
                    SELECT
                        name as product_id , web_item_name as product_name , description ,website_image , item_group as category , brand
                    FROM 
                        `tabWebsite Item` 
                    WHERE
                        name = '{product['product_id']}'
                    """
                website_data= frappe.db.sql(sql_website,as_dict=1)
                for data in website_data:
                    data["qty_bin"] = get_qty_bin(product["item_code"] , get_warehouse())
                    data["price"] = get_item_price(product["item_code"] , get_price_list())
                    data["gallaries"] = get_gallaries(product["slideshow"])
                    data["colors"] = get_colors(product["item_code"])
                    names.append(data)
                
        elif website_item.variant_of != None:
            sql_website = f"""
                    SELECT
                        name as product_id , web_item_name as product_name , description ,
                        website_image , item_group as category , brand
                    FROM 
                        `tabWebsite Item` 
                    WHERE
                        name = '{website_item.name}'
                    """
            website_data= frappe.db.sql(sql_website,as_dict=1)
            for data in website_data:
                data["qty_bin"] = get_qty_bin(website_item.item_code , get_warehouse())
                data["price"] = get_item_price(website_item.item_code , get_price_list())
                data["gallaries"] = get_gallaries(website_item.slideshow)
                data["colors"] = get_colors(website_item.item_code)
                names.append(data)

        return names

    except :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Not exist"

def get_colors(item):
    colors = []
    sql = f'''
            SELECT 
                attribute_value
            FROM
                `tabItem` I
            INNER JOIN 
                `tabItem Variant Attribute` VI
            ON
                I.name = VI.parent
            WHERE
                I.name = '{item}'
                AND
                VI.attribute = "Colour"        
            '''
    color_data= frappe.db.sql(sql,as_dict=1)
    for color in color_data :
        colors.append(color["attribute_value"])
    return colors


def get_gallaries(gallary):
    images=[]
    sql = f'''
            SELECT 
                image
            FROM 
                `tabWebsite Slideshow`  S
            INNER JOIN 
                `tabWebsite Slideshow Item` SI
            ON
                S.name = SI.parent
            WHERE
                S.name = '{gallary}'
            '''
    image_data= frappe.db.sql(sql,as_dict=1)
    base_url = frappe.utils.get_url()
     
    for image in image_data :
        images.append(f"{base_url}"+image["image"])
    return images

    


def get_item_price(item , price_list):
    sql_price = f""" SELECT price_list_rate FROM `tabItem Price` WHERE item_code ='{item}' AND price_list = '{price_list}' order by creation desc limit 1 """
    price= frappe.db.sql(sql_price,as_dict=1)
    if price and len(price) > 0 :
        price = price[0]["price_list_rate"]
    return price

def get_qty_bin(item , default_warehouse):
    sql_bin = f""" SELECT IFNULL(SUM(actual_qty),0.0 )as qty FROM `tabBin` WHERE item_code ='{item}' and warehouse='{default_warehouse}' """
    qty_bin= frappe.db.sql(sql_bin,as_dict=1)
    
    if qty_bin and len(qty_bin) > 0 :
        qty_bin = qty_bin[0]["qty"]
    return qty_bin



@frappe.whitelist(allow_guest = True)
def products(**args):

    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    
    # if not get_warehouse() or not get_price_list(): (or) not price list only
    if not get_warehouse() or not get_price_list():
        return []
    
    conditions = "1 = 1"
    if 'category' in args and args['category']:
        conditions += f" and i.item_group = '{args['category']}'"
    if 'start' in args and args["start"] :
        conditions += f" and (SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.item_code ORDER BY creation DESC LIMIT 1) >= {float(args['start'])} "
    if 'end' in args and args["end"] :
        conditions += f" and IFNULL((SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.item_code  ORDER BY creation DESC LIMIT 1), 0.0) <= {float(args['end'])}"
    if 'search' in args and args['search']:
        search_term = args['search']
        conditions += f" AND (i.web_item_name LIKE '%{search_term}%' OR i.  LIKE '%{search_term}%') "
    
    sort_by_price = ""
    if 'sort_by_price' in args and args['sort_by_price']:
        sort_by_price += f"  order by price {args['sort_by_price']} "
         
    sql = f'''
            SELECT 
                i.name as product_id ,i.web_item_name as product_name , i.website_image ,
                IFNULL(
                    (SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.item_code and price_list="{get_price_list()}" ORDER BY creation DESC LIMIT 1),
                    0.0) 
                    as price ,
                (g.name) as category_id , g.item_group_name as category
            FROM
                `tabWebsite Item` i
            INNER JOIN 
                `tabItem Group` g
            ON 
                i.item_group = g.name
            WHERE
               (i.has_variants = 1
                or 
                i.variant_of is not null  )
                and
                IFNULL((SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.item_code ORDER BY creation DESC LIMIT 1), 0.0) > 0 
                and
                {conditions}
            {sort_by_price}
            '''
    products= frappe.db.sql(sql , as_dict = 1) 
    base_url = frappe.utils.get_url()
    for product in products :
        if product["website_image"] :
            product["website_image"] = f"{base_url}"+product["website_image"]
    return products



# @frappe.whitelist(allow_guest = True)
# def product(**args):
#     conditions = "1 = 1"
#     if 'category' in args and args['category']:
#         conditions += f" and i.item_group = '{args['category']}'"
#     if 'start' in args and args["start"] :
#         conditions += f" AND IFNULL((SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.name ORDER BY creation DESC LIMIT 1), 0.0) >= {float(args['start'])} "
#     if 'end' in args and args["end"] :
#         conditions += f" AND IFNULL((SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.name ORDER BY creation DESC LIMIT 1), 0.0) <= {float(args['end'])} "  
#     if 'search' in args and args['search']:
#         search_term = args['search']
#         conditions += f" AND (i.item_name LIKE '%{search_term}%' OR i.description LIKE '%{search_term}%') "



#     if 'sort_by_price' in args and args['sort_by_price']:
#         conditions += f"  order by price {args['sort_by_price']} "
         
#     sql = f'''
#             SELECT 
#                 i.name as product_id , i.image , IFNULL((SELECT price_list_rate FROM `tabItem Price` WHERE item_code = i.name ORDER BY creation DESC LIMIT 1), 0.0) as price , i.offer,
#                 (g.name) as category_id , g.item_group_name as category
#             FROM
#                 `tabItem` i
#             INNER JOIN 
#                 `tabItem Group` g
#             ON 
#                 i.item_group = g.name
#             WHERE
#                 {conditions}
#             '''
#     product = frappe.db.sql(sql , as_dict = 1) 
#     for entry in product :
#         return entry