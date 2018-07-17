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


def update_barcode_member():
    barcode_rule_id = openerp.BarcodeRule.browse(
                [('for_type_A_capital_subscriptor', '=', True)], limit=1)
    print '\n\n>>>>', barcode_rule_id
    if barcode_rule_id and barcode_rule_id.generate_type[0] == 'sequence':
        partners = openerp.ResPartner.browse([
            ('is_member', '=', True),
            ('barcode_rule_id.for_associated_people', '=', True),
            ])
        print '\n\n>>>>>>>members', partners
        for partner in partners:
            partner.barcode_rule_id = barcode_rule_id.id[0]
            partner.generate_base()
            partner.generate_barcode()
    return True


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    update_barcode_member()
