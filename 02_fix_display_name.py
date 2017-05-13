#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import datetime
import time
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
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])


###############################################################################
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################

partners = openerp.ResPartner.browse([])

print "found %d partners" % len(partners)
count = 0

for partner in partners:
    count += 1
    if count % 100 == 0:
        print "managed %d" % count
    partner.name = partner.name
