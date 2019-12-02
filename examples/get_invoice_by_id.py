#!/usr/bin/python

from odoo_automation import Odoo

from settings import odoo_url, odoo_db, odoo_user, odoo_password

o = Odoo(url = odoo_url, db = odoo_db, user = odoo_user, password =
         odoo_password)

invoice_id = 16
print(o.get_invoice_by_id(invoice_id))
