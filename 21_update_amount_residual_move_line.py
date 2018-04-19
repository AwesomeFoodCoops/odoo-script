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


def update_fields_amount_residual_of_move_line():
    account_ids = openerp.AccountAccount.search(
        [('reconcile', '=', True)], order='id')
    print ">>>>>>>>account_ids:", account_ids
    for account_id in account_ids:
        print ">>>>>>>>account_id:", account_id
        journal_items = openerp.AccountMoveLine.browse(
            [('account_id', '=', account_id),
             ('reconciled', '=', False),
             ('amount_residual', '=', 0)], order='id')
        # Update residual amount for these items
        print ">>>>>>>> Start updating Data <<<<<<<<<"
        for journal_item in journal_items:
            journal_item.move_id.state = journal_item.move_id.state
        print ">>>>>>>> Updating Data completed <<<<<<<<"
    return True


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    update_fields_amount_residual_of_move_line()
