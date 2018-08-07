#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
from cfg_secret_configuration import odoo_configuration_user
import time


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

def create_member_space_user():
    members = openerp.ResPartner.browse(
        [('is_member', '=', True), ('email', '!=', False)]
    )
    members.create_memberspace_user()

# Run the create function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    create_member_space_user()
