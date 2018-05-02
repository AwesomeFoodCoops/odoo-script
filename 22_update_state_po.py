#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
from cfg_secret_configuration import odoo_configuration_user


###############################################################################
# Odoo Connection
###############################################################################
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz, database


openerp, uid, tz, db = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

###############################################################################
# Script
###############################################################################


def update_state_of_purchase_order():
    po_ids = [273]
    purchases = openerp.PurchaseOrder.browse(
        [('state', '=', 'purchase'),
         ('order_line', '=', False),
         ('id', 'in', po_ids)], order='id')
    print ">>>>>>>>purchases:", purchases
    # Update state of purchase order
    print ">>>>>>>> Start updating Data <<<<<<<<<"
    for purchase in purchases:
        print ">>>>>>>>purchase:", purchase
        purchase.state = 'draft'
        print ">>>>>>>>state:", purchase.state
    print ">>>>>>>> Updating Data completed <<<<<<<<"
    return True


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    update_state_of_purchase_order()
