#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Ticket S#12692: Unable to allocate with Write-Off on acc. 511200

    Issue:
        Accounting move lines, filter on account 511200
        select lines Options/Allocate lines with posting difference
        Use journal CCOOP as counterpart and validate => An account
        move is created and allocated but debit/credit = "0"
'''
from cfg_secret_configuration import odoo_configuration_user
import erppeek

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


def fix_journal_item_residual_amount():
    '''
    Function to update residual amount of Journal Items of
        - Account 511200
        - Not reconciled
        - Items with Residual Amount = 0

    to Debit value of that journal item
    '''

    # Searching for the to-be-updated journal items
    account_ids = openerp.AccountAccount.search([('code', '=', '511200')])
    if not account_ids:
        print ">>>>>>>> Account with code 511200 cannot be found <<<<<<<<<<"
        return False

    account_id = account_ids[0]
    journal_item_domain = [('account_id', '=', account_id),
                           ('amount_residual', '=', 0),
                           ('reconciled', '=', False)]
    journal_items = openerp.AccountMoveLine.browse(journal_item_domain)
    print ">>>>>>>> Number of Journal Item found: ", len(journal_items)

    # Update residual amount for these items
    print ">>>>>>>> Start updating Data <<<<<<<<<"
    for item in journal_items:
        # Trigger to recompute the amount residual
        item.move_id.state = item.move_id.state

    print ">>>>>>>> Updating Data completed <<<<<<<<"


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    fix_journal_item_residual_amount()
