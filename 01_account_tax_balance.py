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

# Quantity of moves to batch at the same time
MOVE_QTY_TO_BATCH = 1000

# Pause duration between two batches
SLEEP_TIME = 0.0

###############################################################################
# Script
###############################################################################

print "Found %d moves to compute" % (
    openerp.count('account.move', [('move_type', '=', False)]))

count = 0

while openerp.count('account.move', [('move_type', '=', False)]) > 0:
    # Get moves to compute
    print "%s : Manage %d - %d moves." % (
        str(datetime.datetime.today()), count, count + MOVE_QTY_TO_BATCH)
    move_ids = openerp.search(
        'account.move', [('move_type', '=', False)], limit=MOVE_QTY_TO_BATCH)
    moves = openerp.AccountMove.browse([('id', 'in', move_ids)])
    moves.compute_move_type()
    count += MOVE_QTY_TO_BATCH
    time.sleep(SLEEP_TIME)
