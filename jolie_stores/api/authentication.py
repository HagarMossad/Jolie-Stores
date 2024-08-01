import requests
import frappe
from frappe import _

def get_token():
    authentication_doc = frappe.get_single("Authentication Setting")
    base_ul = frappe.get_doc("Integration System" , "RTX")
    token_url = f"{base_ul.get('base_url')}{authentication_doc.endpoinet}"
    data = {
        "username" : authentication_doc.user,
        "password" : authentication_doc.password
    }
    response = requests.post(token_url, data)
    data = response.json()
    authentication_doc.db_set("token",data.get('token')) 
    authentication_doc.save()
    frappe.db.commit()
    print({"token" : authentication_doc.token , "base_url" :base_ul.get('base_url') })
    return {"token" : authentication_doc.token , "base_url" :base_ul.get('base_url') }
