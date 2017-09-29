#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Ticket S#14202
    Content:
    - Update product to use theoretical cost and theoretical price

'''
from cfg_secret_configuration import odoo_configuration_user
import erppeek
import sys

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


def update_product_template():
    '''
    @Function to update product and make the report for the impact
    '''
    products = openerp.ProductTemplate.browse([])
    product_len = len(products)
    product_counter = 0
    print "===== Start Updating Product ====="
    for product in products:
        product_counter += 1
        sys.stdout.write("\rCompleted: %d / %d" % (
            product_counter, product_len))
        sys.stdout.flush()

        theo_price_prod_list = [u"Product ID|Barcode|Default Code|" +
                                "Product Name|Sale Price|Theoritical " +
                                "Price VAT Incl."]
        theo_cost_prod_list = [u"Product ID|Barcode|Default Code|" +
                               "Product Name|Cost|Theoritical " +
                               "Cost"]

        # Update theoretical price
        if product.list_price != product.theoritical_price:
            theo_price_prod_list.append(u"%d|%s|%s|%s|%f|%f" % (
                product.id, product.barcode, product.default_code,
                product.name, product.list_price, product.theoritical_price))

            # product.write({'list_price': product.theoritical_price})
            product.use_theoritical_price()

        # Update theoretical price
        if product.standard_price != product.coeff9_inter_sp:
            theo_cost_prod_list.append(u"%d|%s|%s|%s|%f|%f" % (
                product.id, product.barcode, product.default_code,
                product.name, product.standard_price, product.coeff9_inter_sp))

            # product.write({'standard_price': product.coeff9_inter_sp})
            product.use_theoritical_cost()

    print "===== Start Generating Report ====="

    with open("Price Update.csv", "w") as price_update_file:
        price_data = u"\n".join(theo_price_prod_list)

        # write it to file
        price_update_file.write(price_data.encode('utf8'))

    with open("Cost Update.csv", "w") as cost_update_file:
        cost_data = u"\n".join(theo_cost_prod_list)

        # write it to file
        cost_update_file.write(cost_data.encode('utf8'))

    print "===== DONE ====="


update_product_template()
