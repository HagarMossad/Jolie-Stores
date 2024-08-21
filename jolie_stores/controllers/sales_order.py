from jolie_stores.api.authentication import get_token
import requests
import frappe

def submit_order(self , event):
    data = {
    "full_name": self.user_name,
    "phone": self.user_phone,
    "address": self.user_address,
    "total_amount": self.total + self.fees,
    "notes": self.notes,
    "order_date": str(self.date_time),
    "shipment_contents": ' '.join([f'{item.item_code} x {item.qty} / ' for item in self.items])[:-2],
    "weight": "0.5",
    "reference_id" : self.name,
    "city": int(frappe.get_doc("City" , self.city).id),
    "total_fees" : self.fees
    }
    token = get_token()["token"]
    url = f'{get_token()["base_url"]}/integration/order'
    print(url)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=headers)
    data = response.json()

def calculate_fees(self , event):
    if self.fees :
        self.grand_total +=self.fees