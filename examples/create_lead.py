#!/usr/bin/python

from odoo_automation import Odoo

from settings import odoo_url, odoo_db, odoo_user, odoo_password

o = Odoo(url = odoo_url, db = odoo_db, user = odoo_user, password =
         odoo_password)

o.logger.info('Creating lead in Odoo....')
print(o.create_lead('lead name created from API 3',
                    'description created from API'))
