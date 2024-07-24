import frappe

@frappe.whitelist(allow_guest=True)
def city():
    if frappe.local.request.method != "GET":
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "Only GET method is allowed"
        return
    city= frappe.db.sql('select city_name,fees from `tabCity`' , as_dict=1)
    if city :
        return city
    else :
        frappe.local.response['http_status_code'] = 404 
        frappe.local.response['data'] = "No city created"
    
