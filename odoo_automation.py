#!/usr/bin/python3

from logging import getLogger, INFO, StreamHandler, Formatter, FileHandler
from sys import stdout
from xmlrpc import client
from datetime import datetime
from base64 import b64decode
from xmlrpc.client import Fault

class Odoo():

    def __init__(self, url = None, db = None,  user = None, password = None):
        self.logger = self._setup_logger('odoo', 'stdout')
        self.url = url
        self.db = db
        self.user = user
        self.password = password
        self.common = None
        self.models = None
        self.uid = None
        self.invoices_ids = None
        self.l_invoices_issued = []
        # hardcoded
        self.date_format = '%Y-%m-%d %H:%M:%S'
        self.invoice_type = False

    def _login(self):
        '''
        Login to Odoo through its API
        '''
        self.common = client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        self.uid = self.common.authenticate(self.db, self.user,
                                    b64decode(self.password).decode('utf8'),{})

    def _get_models(self):
        '''
        Returns Odoo API models object
        '''
        self.models = client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

    def _execute_kw(self, model, method, params, opt_params = None):
        '''
        Wrapper for models.execute_kw
        '''
        if opt_params:
            return self.models.execute_kw(self.db, self.uid,
                                       b64decode(self.password).decode('utf8'),
                                          model, method, params, opt_params)
        else:
            return self.models.execute_kw(self.db, self.uid,
                                       b64decode(self.password).decode('utf8'),
                                          model, method, params)

    def _get_vat_by_name(self, name):
        '''
        Returns corresponding VAT number from client's name
        '''
        partner_id = self._get_partner_id_by_name(name)
        opt_params = {
            'fields': ['vat'],
        }
        return self._execute_kw('res.partner', 'read',
                                [partner_id], opt_params)[0]['vat']

    def _get_partner_id_by_name(self, name):
        '''
        Returns client ID given its name
        '''
        return self._execute_kw('res.partner', 'search',
                                [[['name', '=', name]]])
 
    def _add_vat_to_invoice_list(self):
        '''
        Adds VAT correspondiing to 'partner_display_name'
        '''
        vat = None
        new_l_invoices_issued = []
        for invoice in self.l_invoices:
            invoice['vat'] = self._get_vat_by_name(
                                       invoice['invoice_partner_display_name'])
            del invoice['id']
            new_l_invoices_issued.append(invoice)
        return new_l_invoices_issued
            
    def _setup_logger(self, name, log_file, level=INFO):
        # https://stackoverflow.com/a/11233293
        '''
        Creates a logger
        '''
        if log_file == 'stdout':
            formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler = StreamHandler(stdout)
        else:
            formatter = Formatter('%(asctime)s %(message)s')
            handler = FileHandler(log_file)
        handler.setFormatter(formatter)
        logger = getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def _get_lead_next_id(self):
        '''
        Return last id of crm.lead model
        '''
        params = [[]]
        try:
            return max(self._execute_kw('crm.lead', 'search', params)) + 1
        # TODO: make sure that no crm leads exception is being catched here
        except Fault as e:
            return 0
        # Special case: 0 leads
        except ValueError as e:
            return 0

    def create_lead(self, name, description):
        '''
        Create a lead in Odoo
        '''
        self._login()
        self._get_models()
        # I realized that passing always 0 it works, so skipping one step
        #lead_id = self._get_lead_next_id()
        lead_id = 0
        now_str = datetime.now().strftime(self.date_format)
        params = [{
           'id': lead_id,
           'name': name,
           'active': 't',
           'description': description,
           'type': 'opportunity',
           'date_open': now_str,
           'date_last_stage_update': now_str,
           'create_date': now_str,
        }]
        return(self._execute_kw('crm.lead', 'create', params))

    def _get_leads_with_some_fields(self, l_fields):
        '''
        Return list of CRM leads. Fields is a list of crm_lead fields
        '''
        if not self.uid:
            self._login()
            self._get_models()
        leads_ids = self._execute_kw('crm.lead', 'search', [[]])
        if leads_ids:
            opt_params = {
                'fields': l_fields,
            }
            return self._execute_kw('crm.lead', 'read',
                                    [leads_ids], opt_params)
        return None

    def get_invoices(self, invoice_type, fields, is_add_vat = True):
        '''
        Returns invoices issued ('out_invoice') or supported ('in_invoice')
        '''
        self._login()
        self._get_models()
        self.invoice_type = invoice_type
        self.invoices_ids = self._get_invoices_ids()
        self.l_invoices = self._get_invoices(fields)
        if is_add_vat:
            return(self._add_vat_to_invoice_list())

    def _get_invoices_ids(self):
        '''
        Returns ids of invoices issued or supported
        '''
        params = [[['type', '=', self.invoice_type], ['state', '=', 'posted']]]
        # IMPORTANT: the order of the list is determined here
        sortBy = "date asc, amount_untaxed desc"
        opt_params = {
            'order': sortBy,
        }
        return self._execute_kw('account.move', 'search', params, opt_params)

    def _get_invoices(self, fields):
        '''
        Returns list of invoices issued or supported with fields
        '''
        opt_params = {
            'fields': fields,
        }
        return self._execute_kw('account.move', 'read',
            [self.invoices_ids], opt_params)

