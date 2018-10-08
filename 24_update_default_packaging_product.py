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


def update_default_packaging_product():
    product_templates = openerp.ProductTemplate.browse([])
    for product_template in product_templates:
        package_qty = product_template.seller_ids and\
            product_template.seller_ids[0].package_qty
        if product_template.default_packaging != package_qty and package_qty and package_qty > 0:
            product_template.default_packaging = package_qty
    return True


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    update_default_packaging_product()
