import erppeek
import csv
import sys
import logging
from cfg_secret_configuration import odoo_configuration_user


###############################################################################
# QUICK GUIDE
# Run command:
# python import_initial_inventory.py [CSV PATH] [INVENTORY ID]
# or
# python import_initial_inventory.py [CSV PATH] [INVENTORY ID] [OUTPUT LOG FILE]
#
# Ex:
# python import_initial_inventory.py ./produits_initiale.csv 1234 debug.txt
# or
# python import_initial_inventory.py ./produits_pour_maj_initiale.csv 1234
#
###############################################################################

input_file = sys.argv[1]
inventory_db_id = int(sys.argv[2])
print inventory_db_id
try:
    log_file = sys.argv[3]
    if log_file:
        logging.basicConfig(filename=log_file,level=logging.DEBUG)
except:
    log_file = False


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
# End Odoo Connection
###############################################################################

def print_log(msg, error=False):
    str_msg = ""
    if error:
        str_msg = "[LOG] - [ERROR] - "
    else:
        str_msg = "[LOG] - [DEBUG] - "
    str_msg += msg
    print str_msg
    if log_file:
        if error:
            logging.error(msg)
        else:
            logging.info(msg)


def import_inventory_data():
    '''
    Import initial inventory value for new database.
    Just only import quantity on hands.
    Prepare data :
    - Default location : stock.stock_location_stock
    - NO Inventory Adjustment is confirming or draft.
    - Input file have to be CSV file and have 2 columns 'id' and 'stock'
    '''
    ir_model_data = openerp.model('ir.model.data')
    stock_inv_model = openerp.model('stock.inventory')
    prod_prod_model = openerp.model('product.product')
    stock_inv_line_model = openerp.model('stock.inventory.line')

    # Reading the file and prepare the inventory data
    inventory_line_data = {}

    has_error = False

    print "====== CHECKING INPUT FILE ========="
    with open(input_file, 'r') as inv_file:
        f = csv.reader(
            inv_file, delimiter=';', quotechar='"')
        count = 0
        header = {}
        for line in f:
            count += 1
            # first line include header
            # Finding the vendor supplier info on vendor product code
            if count == 1:
                for idx, head in enumerate(line):
                    header.update({head: idx})
                if 'id' not in header:
                    has_error = True
                    raise ValueError("Error ! No field named as 'id'")
                if 'stock' not in header:
                    has_error = True
                    raise ValueError("Error ! No field named as 'stock'")
                continue
            if len(header) != len(line):
                print_log("Incorrect format for line "
                          "%d - %d : %d" % (count, len(header), len(line)),
                          True)
                continue

            product_id = line[header['id']]
            quantity = 0.0
            if not line[header['stock']] \
               or not line[header['stock']].isdigit() \
               or float(line[header['stock']]) < 0:
                print_log("Line %d has invalid quantity." % count, True)
                continue
            else:
                quantity = float(line[header['stock']])
            try:
                module_name, record_name = product_id.strip().split('.')
                if not module_name or not record_name:
                    raise ValueError("Incorrect 'id'."
                                     "Its format should be __export__.id")

                # check record name is product.product or product.template
                if 'product_product' in record_name:
                    _, prd_id =  \
                        ir_model_data.get_object_reference(module_name,
                                                           record_name)
                elif 'product_template' in record_name:
                    _, prd_tmpl_id = \
                        ir_model_data.get_object_reference(module_name,
                                                           record_name)
                    if not prd_tmpl_id:
                        print_log("Line %d is incorrect : cannot find"
                                  "product template id %s " % (count, product_id),
                                  True)
                        has_error = True
                        continue
                    prd_id = prod_prod_model.search(
                        [('product_tmpl_id', '=', prd_tmpl_id)], limit=1)
                    prd_id = prd_id and prd_id[0]
                else:
                    raise ValueError("Incorrect 'id'."
                                     "This tool only support for product.")


                if not prd_id:
                    print_log("Line %d is incorrect : cannot find"
                              "product for id %s " % (count, product_id), True)
                    has_error = True
                    continue
                if prd_id not in inventory_line_data:
                    inventory_line_data[prd_id] = quantity
            except ValueError:
                print_log("Line %d : Incorrect 'id'."
                          "Its format should be __export__.id - "
                          "found %s " % (count, product_id), True)
                raise ValueError("Incorrect 'id'."
                                 "Its format should be __export__.id")
            except AttributeError:
                print_log("Line %d : Incorrect type of 'id'."
                    "Its format should be unicode with __export__.id - "
                    "found %s " % (count, str(type(product_id))),
                    True)
                raise AttributeError("Incorrect type of 'id'."
                    "Its format should be unicode with __export__.id")
        print "Successfully checking  %d lines" % count

    # Check File before importing
    if inventory_line_data and not has_error:
        print "====== IMPORT INITIAL INVENTORY ========="
        # lock database to import
        inventory_id = stock_inv_model.browse(inventory_db_id)
        if inventory_id.state == 'draft':
            inventory_id.prepare_inventory()
        if inventory_id.state in ['cancel', 'done']:
            print_log("Existed Inventory Adjustment was validated", False)
            print_log("Force Quit from initial Inventory.", False)
            return

        # get list current products
        added_prds = {}
        for line in inventory_id.line_ids:
            added_prds.update({line.product_id.id: line})
        for prd_db_id, quantity in inventory_line_data.iteritems():
            # Searching the owner of the product
            product = prod_prod_model.browse(prd_db_id)
            if product.id not in added_prds:
                new_line = stock_inv_line_model.create(
                    {'inventory_id': inventory_id.id,
                     'product_id': prd_db_id,
                     'product_qty': quantity,
                     'location_id': inventory_id.location_id.id,
                     'product_uom_id': product.uom_id.id}
                )
                added_prds.update({new_line.product_id.id: new_line})
            else:
                line = added_prds[prd_db_id]
                line.write({'product_qty': quantity,})
            print_log("Import successfully inventory value "
                      "for %s " % product.product_tmpl_id.name,
                      False)
        print_log("Import successfully initial inventory value for"
                  " %d products." % len(inventory_line_data), False)

import_inventory_data()
