
import frappe

def after_install():
    create_domain_list()

def create_domain_list():
	if not frappe.db.exists("Domain", "IFI"):
		dm1 = frappe.new_doc("Domain")
		dm1.domain = 'IFI'
		dm1.insert()