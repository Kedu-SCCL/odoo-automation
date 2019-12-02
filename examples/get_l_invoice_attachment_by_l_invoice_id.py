#!/usr/bin/python

from odoo_automation import Odoo

from settings import odoo_url, odoo_db, odoo_user, odoo_password

o = Odoo(url = odoo_url, db = odoo_db, user = odoo_user, password =
         odoo_password)

l_invoice_supported_ids = o._get_invoices_ids('in_invoice')
print(o.get_l_invoice_attachment_by_l_invoice_id(l_invoice_supported_ids))
