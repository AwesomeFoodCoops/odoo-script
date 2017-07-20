#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Ticket S#12994: Member Refactoring
    Content:
    - Update partner owned shares

'''
from cfg_secret_configuration import odoo_configuration_user
import erppeek
import sys

###############################################################################
# Odoo Connection
###############################################################################


def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

###############################################################################
# Script
###############################################################################


def update_partner_owned_share():
    '''
    @Function run by erppeek to update data for partner owned shares
    '''
    print ">>>>>>> START UPDATING PARTNER OWNED SHARES >>>>>>>>>>"
    # Search for all invoice with fundraising_category_id set
    invoices = openerp.AccountInvoice.browse(
        [('fundraising_category_id', '!=', False),
         ('partner_owned_share_id', '=', False)])

    total_inv = len(invoices)
    counter = 0
    print ">>>> Number of Invoices found: %d" % total_inv
    for invoice in invoices:
        invoice.assign_ownshare_to_invoice()
        counter += 1
        sys.stdout.write("\rCompleted: %d / %d" % (counter, total_inv))
        sys.stdout.flush()

    print "\n>>>>>>> DONE >>>>>>>>>>"


update_partner_owned_share()
