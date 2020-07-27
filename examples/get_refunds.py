#!/usr/bin/python

from odoo_automation import Odoo

from settings import odoo_url, odoo_db, odoo_user, odoo_password

o = Odoo(url = odoo_url, db = odoo_db, user = odoo_user, password =
         odoo_password)

fields = ('name', 'date', 'invoice_partner_display_name',
          'amount_untaxed', 'amount_tax', 'amount_total',
                      'invoice_payment_state')
print(o.get_invoices('in_refund', fields))
