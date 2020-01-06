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


def validate_pickings(order_ids):
    for order in openerp.PosOrder.browse([('id', 'in', order_ids)]):
        picking_ids = openerp.search(
            'stock.picking', [('origin', '=', order.name),
                              ('state', '=', 'draft')])
        print('order, pickings::::', order, picking_ids)
        for picking in \
                openerp.StockPicking.browse([('id', 'in', picking_ids)]):
            move_list = []
            for line in order.lines:
                if line.product_id and \
                        line.product_id.type not in ['product', 'consu']:
                    continue
                move_id = openerp.StockMove.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': picking.id,
                    'picking_type_id': picking.picking_type_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                })
                move_list.append(move_id)
            order.write({'picking_id': picking.id})
            picking.action_assign()
            picking.force_assign()
            # Mark pack operations as done
            for pack in picking.pack_operation_ids:
                if pack.product_id.tracking == 'none':
                    pack.write({'qty_done': pack.product_qty})
            if not any([(x.product_id.tracking != 'none') for x in
                        picking.pack_operation_ids]):
                picking.action_done()
    return True


if not openerp:
    print(">>>>>>>> Cannot connect to Server <<<<<<<<<")
else:
    order_ids = openerp.search(
        'pos.order', [('picking_id', '=', False),
                      ('state', 'in', ('paid', 'done', 'invoiced'))])
    for orders in zip(*[iter(order_ids)]*100):
        print(orders)
        validate_pickings(orders)
