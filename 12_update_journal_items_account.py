#! /usr/bin/env python
# -*- encoding: utf-8 -*-

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


def correct_account_on_journal_item(correct_data=False):
    '''
    Function to update account on journal item
    Process:
        Step 1: Search for journal items of related accounts
        Step 2: Get Payment of the journal
        Step 3: Cancel the payment and set the Payment Account ID to the
        correct one.
        Step 4: Validate the payment
    '''
    from_account_code = [
        '403001', '403002', '403003', '403004', '403005', '403006',
        '403007', '403008', '403009', '403010', '403011', '403012',
    ]
    to_account_code = '403000'
    payment_list = []

    from_account_ids = openerp.AccountAccount.search(
        [('code', 'in', from_account_code)])

    if len(from_account_ids) != len(from_account_code):
        print ">>>>> Some from accounts cannot be found"

    to_account = openerp.AccountAccount.browse(
        [('code', '=', to_account_code)])

    if not to_account:
        print ">>>>> Account %s cannot be found" % to_account_code

    # Search for the journal items of given accounts
    journal_items = openerp.AccountMoveLine.browse(
        [('account_id', 'in', from_account_ids)])

    for jour_item in journal_items:
        payment = jour_item.payment_id
        if not payment:
            print "===== Item %s: Payment cannot be found" % jour_item.name
        else:
            payment_list.append(payment)

    # Correct data part
    if not correct_data:
        return

    deprecated = to_account[0].deprecated

    to_account[0].deprecated = False

    report_data = [
        "ID|Payment Name|New Payment Name|From Account Code|To Account Code"]
    for payment in payment_list:
        print "=== Payment: ", payment
        payment_name = payment.name
        source_account = payment.payment_account_id.code

        # Cancel the payment
        payment.cancel_payment()

        # Set the payment account id to 403000
        payment.payment_account_id = to_account[0].id

        # Validate the payment
        payment.post_payment()

        rdata = [str(payment.id), payment_name, payment.name,
                 source_account, to_account_code]

        report_data.append(u"|".join(rdata))

    to_account[0].deprecated = deprecated

    # Write the reporting data to file
    with open("account_update_report.csv", "w") as f:
        data = u"\n".join(report_data)

        # write it to file
        f.write(data.encode('utf8'))


correct_account_on_journal_item(correct_data=True)
