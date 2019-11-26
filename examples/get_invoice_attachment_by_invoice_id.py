#!/usr/bin/python

from odoo_automation import Odoo

from settings import odoo_url, odoo_db, odoo_user, odoo_password

o = Odoo(url = odoo_url, db = odoo_db, user = odoo_user, password =
         odoo_password)

ids = [432]
print(o.get_invoice_attachment_by_invoice_id(ids))
