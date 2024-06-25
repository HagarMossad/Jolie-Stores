

import requests
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True) 
def update_api_token():
    authentication_setting = frappe.get_single("Authentication Setting")
    url = f"{authentication_setting.endpoinet}"

    payload = {
        "username": f"{authentication_setting.user}",
        "password": f"{authentication_setting.password}"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Check if the request was successful

        data = response.json()
        token = data.get('refresh')
        return token

        if token:
            # Fetch the existing API Token document or create a new one
            doc = frappe.get_doc("API Token", "API Token")  # Assuming you have a single document
            if not doc:
                doc = frappe.new_doc("API Token")
            doc.token = token
            doc.save()
            frappe.db.commit()
            return _("Token updated successfully")
        else:
            return _("Failed to retrieve token from the response")
    except requests.exceptions.RequestException as e:
        frappe.log_error(message=str(e), title="External API Error")
        return _("Failed to fetch token from the external API")
    

