from jolie_stores.api.authentication import get_token
import requests
import frappe

def submit_order(self , event):
    data = {
    "full_name": self.user_name,
    "phone": self.user_phone,
    "address": self.user_address,
    "total_amount": self.total,
    "notes": "note",
    "order_date": self.date_time,
    "shipment_contents": ' '.join([item.item_code for item in self.items]),
    "weight": "50.00",
    "city": int(frappe.get_doc("City" , self.city).id)
    }
    print(data["city"])

    token = get_token()
    url = "http://92.205.177.106:8020/integration/order"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(response)
    print("*"*30)
    data = response.json()

def calculate_fees(self , event):
    if self.fees :
        self.grand_total +=self.fees