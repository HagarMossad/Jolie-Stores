import requests
import frappe
from frappe import _

def get_token():
    authentication_doc = frappe.get_single("Authentication Setting")
    token_url = authentication_doc.endpoinet
    data = {
        "username" : authentication_doc.user,
        "password" : authentication_doc.password
    }
    response = requests.post(token_url, data)
    data = response.json()
    authentication_doc.token =  data.get('token')
    authentication_doc.save()
    return authentication_doc.token
