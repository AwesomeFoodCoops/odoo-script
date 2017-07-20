#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Ticket S#13136: product_history stock shortage
    Content:
    - Update the history to ignored for history line with outgoing = 0

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


def update_ignore_product_history():
    '''
    @Function run by erppeek to update data for product history
    '''
    print ">>>>>>> START UPDATING PRODUCT HISTORY >>>>>>>>>>"
    # Search for all product history with outgoing = 0
    product_histories = openerp.ProductHistory.browse(
        [('outgoing_qty', '=', 0),
         ('ignored', '=', False)])

    total_line = len(product_histories)
    counter = 0
    print ">>>> Number of Product History Lines found: %d" % total_line
    for line in product_histories:
        line.ignore_line()
        counter += 1
        sys.stdout.write("\rCompleted: %d / %d" % (counter, total_line))
        sys.stdout.flush()

    print "\n>>>>>>> DONE >>>>>>>>>>"


update_ignore_product_history()
