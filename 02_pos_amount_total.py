#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import datetime
import time
import erppeek

from cfg_secret_configuration import odoo_configuration_user

# TODO BEFORE RUNNING THIS SCIRPT
#ALTER TABLE pos_order ADD COLUMN amount_total numeric; COMMENT ON COLUMN pos_order.amount_total IS 'Total Amount';
# modify pos.order.line model to store price_subtotal_incl
# https://github.com/shewolfParis/odoo-production/pull/154/files

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
QTY_TO_BATCH = 10

# Pause duration between two batches
SLEEP_TIME = 0.0

###############################################################################
# Script
###############################################################################

t = openerp.count('pos.order', [('amount_total', '=', False)])
print "Found %d orders to compute" % (t)

count = 0

while openerp.count('pos.order', [('amount_total', '=', False)]) > 0:
    print "%s : Manage %d - %d orders (%d p.c.)" % (
        str(datetime.datetime.today()), count, count + QTY_TO_BATCH, count/(t/100.0))
    order_ids = openerp.search(
        'pos.order', [('amount_total', '=', False)], limit=QTY_TO_BATCH)
    orders = openerp.PosOrder.browse([('id', 'in', order_ids)])
    for order in orders:
        currency = order.pricelist_id.currency_id
        total = 0.0
        for line in order.lines :
            total += line.price_subtotal_incl
        order.amount_total = total
    count += QTY_TO_BATCH
    time.sleep(SLEEP_TIME)
