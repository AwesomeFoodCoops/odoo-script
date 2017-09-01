#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Content:
    - Update product label for products

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


def update_product_labels():
    '''
    @Function to update product label for the BIO product
    '''
    product_pattern = 'BIO'
    label_id = 1

    if not label_id:
        print ">>>> Please set the label ID to update in the script >>>>"

    products = openerp.ProductProduct.browse(
        [('name', 'ilike', product_pattern),
         ('scale_group_id', '!=', False)])

    print ">>>>>>>>> Number of product found: ", len(products)

    to_update = raw_input("Update product (y/n/s): ")

    if to_update.upper() == 'Y':
        print ">>>>>>>>>>> START UPDATING <<<<<<<<<<<<"
        products.write({'label_ids': [(4, label_id)]})
        print ">>>>>>>>>>>> UPDATE DONE <<<<<<<<<<<<"
    elif to_update.upper() == 'S':
        print ">>>>>>>>>> SKIPPED <<<<<<<<<<"
    else:
        print ">>>>>>>>>> CANCELLED <<<<<<<<<<<"
        return True


update_product_labels()
