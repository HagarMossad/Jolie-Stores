import frappe 
from frappe.utils import today
from frappe.utils import now
from urllib.parse import urlparse

def get_path(image):
    url = f"{frappe.utils.get_url()}"
    path_with_image = url+image
    return path_with_image

@frappe.whitelist(allow_guest=True)
def create_carts(carts , user ):
    if frappe.local.request.method != "POST":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only POST method is allowed"
        return
    if not carts:
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "No carts provided"
        return

    flag = True
    for cart in carts:
        if 'id' not in cart or 'qty' not in cart: 
            frappe.local.response['http_status_code'] = 404 
            frappe.local.response['data'] = "Invalid cart data"
            return
        sql = f'''
                SELECT 
                   name , item_code , web_item_name as item_name
                FROM
                    `tabWebsite Item`
                WHERE
                    name ='{cart["id"]}'
            '''
        item_code = frappe.db.sql(sql, as_dict=1)
        if item_code :
            cart["item_name"] = item_code[0]["item_name"]
            cart["product_id"] = item_code[0]["name"]
            item_qty = get_qty_bin(item_code[0]["item_code"] , get_warehouse())
            if cart["qty"]  > item_qty:
                flag = False
                cart["avalible_qty"] = item_qty     
        else :
            frappe.local.response['http_status_code'] = 404
            frappe.local.response['data'] = "Invalid ID cart"
            return
    if flag == True :
        create_order(carts=carts , user=user)
        frappe.local.response['http_status_code'] = 200
        frappe.local.response['data'] = "Order Created"
        return
    else :
        frappe.local.response['http_status_code'] = 403
        return carts

@frappe.whitelist(allow_guest=True)
def validate_carts(carts ):
    if frappe.local.request.method != "POST":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only POST method is allowed"
        return
    if not carts:
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "No carts provided"
        return
    list =[]
    for cart in carts:
        if 'id' not in cart or 'qty' not in cart or 'price' not in cart: 
            frappe.local.response['http_status_code'] = 404 
            frappe.local.response['data'] = "Invalid cart data"
            return
        sql = f'''
                SELECT 
                   i.name , i.item_code , i.web_item_name as product_name , i.variant_of , i.item_group , g.item_group_name , i.website_image
                FROM
                    `tabWebsite Item` i
                INNER JOIN 
                    `tabItem Group` g
                ON 
                    i.item_group = g.name
                WHERE
                    i.name ='{cart["id"]}'
            '''
        item_code = frappe.db.sql(sql, as_dict=1)
        if item_code :
            if item_code[0]["variant_of"] :
                website_item_sql = f''' SELECT name , web_item_name as template_name  from `tabWebsite Item` where item_code = '{item_code[0]["variant_of"]}' '''
                website_item = frappe.db.sql(website_item_sql , as_dict = 1)
                cart["template_id"] = website_item[0]["name"]
                cart["product_name"] = website_item[0]["template_name"]
            else :
                cart["template_id"] = item_code[0]["name"]
                cart["product_name"] = item_code[0]["product_name"]

            cart["product_id"] = item_code[0]["name"]
            cart["website_image"] = item_code[0]["website_image"]
            if item_code[0]["website_image"] :
                cart["website_image"] = get_path(item_code[0]["website_image"])
            cart["category_id"] = item_code[0]["item_group"]
            cart["category_name"] = item_code[0]["item_group_name"]
            item_qty = get_qty_bin(item_code[0]["item_code"] , get_warehouse())
            price = get_item_price(item_code[0]["item_code"] , get_price_list()) 
            cart['qty'] = cart['qty']
            cart["stock"] = item_qty 
            cart["price"] = price   
            list.append(cart)
        else :
            frappe.local.response['http_status_code'] = 404
            frappe.local.response['data'] = f"Invalid ID cart for {cart['id']}"
            return
    return list
    
@frappe.whitelist(allow_guest=True) 
def create_order(carts , user):
    sales_order = frappe.new_doc("Sales Order")
    sales_order.customer = "Jolie Store"
    sales_order.user_name = user["name"]
    sales_order.user_phone = user["phone"]
    sales_order.user_email = user["email"]
    sales_order.user_address = user["address"]
    sales_order.city = user["city"]
    sales_order.delivery_date = today()
    sales_order.date_time = now()
    sales_order.company = 'Jolie'
    selling_settings = frappe.get_single("Selling Settings")
    for cart in carts :
        sql = f'''
                SELECT 
                    item_code 
                FROM
                    `tabWebsite Item`
                WHERE
                    name ='{cart["id"]}'
            '''
        item_code = frappe.db.sql(sql, as_dict=1)
        sales_order.append("items" , {"item_code" : item_code[0]['item_code'] , "qty" : cart['qty'] , "warehouse" :selling_settings.default_warehouse})
    sales_order.save(ignore_permissions=True)
    # sales_order.submit()


def get_warehouse():
    selling_settings = frappe.get_single("Selling Settings")
    return selling_settings.default_warehouse

def get_price_list():
    selling_settings = frappe.get_single("Selling Settings")
    return selling_settings.selling_price_list


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
     
    for image in image_data :
        images.append(get_path( image["image"]))
    return images

    

@frappe.whitelist(allow_guest = True)
def get_item_price(item , price_list):
    sql_price = f""" SELECT price_list_rate FROM `tabItem Price` WHERE item_code ='{item}' AND price_list = '{price_list}' order by creation desc limit 1 """
    price= frappe.db.sql(sql_price,as_dict=1)
    if price and len(price) > 0 :
        price = price[0]["price_list_rate"]
    else :
        price = 0.0
    return price

@frappe.whitelist(allow_guest = True)
def get_qty_bin(item , default_warehouse):
    sql_bin = f""" SELECT IFNULL(SUM(actual_qty + ordered_qty - reserved_qty),0.0 )as qty FROM `tabBin` WHERE item_code ='{item}' and warehouse='{default_warehouse}' """
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
    
    if not get_warehouse() or not get_price_list():
        return []
    
    conditions = "1 = 1"
    if 'category' in args and args['category']:
        conditions += f" and i.item_group = '{args['category']}'"
    if 'search' in args and args['search']:
        search_term = args['search']
        conditions += f" AND (i.web_item_name LIKE '%{search_term}%' OR g.item_group_name  LIKE '%{search_term}%') "

    sql = f'''
            SELECT 
                i.name as product_id ,i.has_variants , i.item_code , i.web_item_name as product_name , i.website_image ,
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
                i.variant_of is null  )
                and
                {conditions}
            '''
    products= frappe.db.sql(sql , as_dict = 1) 
    list = []
    for product in products :
        dict = {}
        if product.has_variants :
            sql = f'''
                SELECT 
                     item_code
                FROM
                    `tabWebsite Item`
                WHERE
                    variant_of = '{product.item_code}'
            '''
            variants = frappe.db.sql(sql , as_dict=1)
            if variants :
                for variant in variants :
                    qty = get_qty_bin(variant["item_code"] , get_warehouse())
                    price = get_item_price(variant["item_code"] , get_price_list()) 
                    if qty > 0  and price > 0.0: 
                        dict["product_id"] = product["product_id"]
                        dict["product_name"] = product["product_name"]
                        dict["category_id"] = product["category_id"]
                        dict["category"] = product["category"]
                        dict["website_image"] = product["website_image"]
                        if product["website_image"] :
                            dict["website_image"] = get_path( product["website_image"])
                        dict["price"] = price
                        break
        else :
            qty = get_qty_bin(product["item_code"] , get_warehouse())
            price = get_item_price(product["item_code"] , get_price_list())
            if qty > 0.0 and price > 0.0: 
                dict["product_id"] = product["product_id"]
                dict["product_name"] = product["product_name"]
                dict["category_id"] = product["category_id"]
                dict["category"] = product["category"]
                dict["website_image"] = product["website_image"]
                if product["website_image"] :
                    dict["website_image"] = get_path(product["website_image"])
                dict["price"] = price
        if dict :
            list.append(dict)
    if 'start_price' in args and args["start_price"] :
        list = filter_products_by_price(list , '>=' ,float(args['start_price']))
    if 'end_price' in args and args["end_price"] :
        list = filter_products_by_price(list , '<=' ,float(args['end_price']))
    if 'start_price' in args and args["start_price"] and 'end_price' in args and args["end_price"] :
        list = filter_products_by_price(list ,'between'  , float(args['start_price']) ,float(args['end_price']) )
    if 'sort_by_price' in args and args['sort_by_price'] :
        list = sort_products_by_price(list ,args['sort_by_price'] )
    if 'limit' in args and args['limit']:
        list = list[:int(args['limit'])]
    return list


def filter_products_by_price(products, operator, value1, value2=None):
    if operator == '>=':
        return [product for product in products if product['price'] >= value1]
    elif operator == '<=':
        return [product for product in products if product['price'] <= value1]
    elif operator == 'between' and value2 is not None:
        return [product for product in products if value1 <= product['price'] <= value2]
    else:
        return []
    
def sort_products_by_price(products, order='asc'):
    if order == 'asc':
        return sorted(products, key=lambda x: x['price'])
    elif order == 'desc':
        return sorted(products, key=lambda x: x['price'], reverse=True)
    else:
        return []
    
@frappe.whitelist(allow_guest = True)
def get_product_details(item):
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    website_item = frappe.db.sql(f"select name , has_variants from `tabWebsite Item` where name = '{item}' " , as_dict = 1)  
    if website_item : 
        sql = f'''
            SELECT 
                i.name as template_id , i.item_code , i.web_item_name as template_name , i.slideshow  , i.description, i.website_image ,
                g.name as category_id , g.item_group_name as category_name
            FROM
                `tabWebsite Item` i
            INNER JOIN 
                `tabItem Group` g
            ON 
                i.item_group = g.name
            WHERE
                i.name = '{item}'
        '''
        products = frappe.db.sql(sql, as_dict=1)
        dict = {}
        dict["template_id"] = products[0]["template_id"]
        dict["template_name"] = products[0]["template_name"]
        dict["description"] = products[0]["description"]
        dict["category_id"] = products[0]["category_id"]
        dict["category_name"] = products[0]["category_name"]
        dict["website_image"] = products[0]["website_image"]
        if products[0]["website_image"] :
            dict["website_image"] = get_path(products[0]["website_image"])
        dict["gallary"] = products[0]["slideshow"] 
        if products[0]["slideshow"] :
                dict["gallary"] = get_gallaries(products[0]["slideshow"] )
        variant_list = []
        if website_item[0]["has_variants"] == 1:
            sql = f'''
                SELECT 
                    name as product_id , item_code ,website_image
                FROM
                    `tabWebsite Item`
                WHERE
                    variant_of = '{products[0]["item_code"]}'
            '''
            variants = frappe.db.sql(sql , as_dict=1)
            for variant in variants :
                price = get_item_price(variant["item_code"] , get_price_list()) 
                stock = get_qty_bin(variant["item_code"] , get_warehouse())
                if price >  0.0 and stock > 0.0 :
                    variant_dict = {}
                    variant_dict["image"] = variant["website_image"]
                    if variant["website_image"] : 
                        variant_dict["image"] =get_path(variant["website_image"])
                    variant_dict["price"] = price 
                    variant_dict["product_id"] = variant["product_id"]
                    variant_dict["stock"] = stock
                    sql_variant = f'''
                                    SELECT 
                                        v.attribute , v.attribute_value
                                    FROM 
                                        `tabItem` i
                                    INNER JOIN 
                                        `tabItem Variant Attribute` v
                                    ON
                                        i.name = v.parent   
                                    where i.name = '{variant["item_code"]}'
                                    '''
                    variant_data = frappe.db.sql(sql_variant , as_dict=1)
                    for entry in variant_data :
                        variant_dict[f"{entry['attribute']}"] = f"{entry['attribute_value']}"
                    variant_list.append(variant_dict)
                
            dict["variants"] = variant_list
        else :
            stock = get_qty_bin(products[0]["item_code"] , get_warehouse())
            price =   get_item_price(products[0]["item_code"] , get_price_list()) 
            if price >  0.0 and stock > 0.0 :
                dict["stock"] =  get_qty_bin(products[0]["item_code"] , get_warehouse())
                dict["price"]  = get_item_price(products[0]["item_code"] , get_price_list()) 

        return dict
    else:
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Not exist"