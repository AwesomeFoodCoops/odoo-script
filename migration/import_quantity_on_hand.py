import csv
import erppeek

###############################################################################
# QUICK GUIDE
# Run command:
# python import_quantity_on_hand.py <input_file_path>
# Ex : python import_quantity_on_hand.py input_inventory_adjustment.csv
#
# File input might have 3 columns :
# - id : external_id of product.product or product.template
# - location_id/name : which is full path name of location (none for default stock)
# - stock : quantity of product in stock.
###############################################################################



###############################################################################
# Odoo Connection
###############################################################################
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

def import_inventory_data(host, db, user, pwd, input_file):
    '''
    Import initial inventory value for new database.
    Just only import quantity on hands.
    Prepare data :
    - Default location for default: stock.stock_location_stock
    - Get columns in csv file of product.template: external id, qty_available
    Script do :
    - Create inventory_adjustment record
    - Make it open
    - Import product lines
    '''
    openerp, _, _ = init_openerp(host, user, pwd, db)

    ir_model_data = openerp.model('ir.model.data')
    stock_inv_model = openerp.model('stock.inventory')
    stock_location_model = openerp.model('stock.location')
    prod_prod_model = openerp.model('product.product')
    stock_inv_line_model = openerp.model('stock.inventory.line')
    stock_warehouse_model = openerp.model('stock.warehouse')

    # Reading the file and prepare the inventory data
    inventory_line_data = {}
    locations = []
    has_error = False

    print "====== START MAKE INVENTORY ADJUSTMENT ========="
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
                if 'stock' not in header:
                    has_error = True
                    print("Do not need to import QOH, exit.")
                    return
                continue

            product_id = line[header['id']]
            quantity = 0.0
            if not line[header['stock']] \
               or float(line[header['stock']]) < 0.0:
#                 print line[header['stock']], type(line[header['stock']])
                continue
            else:
                quantity = float(line[header['stock']])
            if "location_id/name" in header and \
               line[header['location_id/name']] not in locations:
                locations.append(line[header['location_id/name']])
            try:
                module_name, record_name = product_id.strip().split('.')
                if not module_name or not record_name:
                    raise ValueError("Incorrect 'id'."
                                     "Its format should be __export__.id")

                # check record name is product.product or product.template
                if 'product_product' in record_name:
                    res = ir_model_data.search_read([('module', '=', module_name),
                                                     ('name', '=', record_name)],
                                                    ['id', 'res_id'])
                    prd_id = res[0]['res_id']
                elif 'product_template' in record_name:
                    res = \
                        ir_model_data.search_read([('module', '=', module_name),
                                                   ('name', '=', record_name)],
                                                  ['id', 'res_id'])
                    if not res:
                        print "-- Skip product has id = ", product_id
                        continue
                    prd_tmpl_id = res[0]['res_id']
                    if not prd_tmpl_id:
                        print("Line %d is incorrect : cannot find"
                              "product template id %s " % (count, product_id))
                        has_error = True
                        continue
                    prd_id = prod_prod_model.search(
                        [('product_tmpl_id', '=', prd_tmpl_id)], limit=1)
                    prd_id = prd_id and prd_id[0]
                else:
                    raise ValueError("Incorrect 'id'."
                                     "This tool only support for product.")


                if not prd_id:
                    print("Line %d is incorrect : cannot find"
                          "product for id %s " % (count, product_id))
                    has_error = True
                    continue
                if prd_id not in inventory_line_data:
                    inventory_line_data[prd_id] = quantity
            except ValueError:
                print("Line %d : Incorrect 'id'."
                      "Its format should be __export__.id - "
                      "found %s " % (count, product_id))
                raise ValueError("Incorrect 'id'."
                                 "Its format should be __export__.id")
            except AttributeError:
                print("Line %d : Incorrect type of 'id'."
                      "Its format should be unicode with __export__.id - "
                      "found %s " % (count, str(type(product_id))))
                raise AttributeError("Incorrect type of 'id'."
                    "Its format should be unicode with __export__.id")
        print "Successfully checking  %d lines" % count
    # Check File before importing
    if inventory_line_data and not has_error:
        print "====== IMPORT INITIAL INVENTORY ========="
        # create new inventory
        location_id = stock_warehouse_model.browse([])[0].lot_stock_id.id
        if locations and len(locations) == 1:
            location_id = stock_location_model.search([('complete_name', 'like', locations[0])])
            location_id = location_id and location_id[0]
        else:
            print "... We have %d stock location in file." % len(locations)
            print "... EXIT!!!"
            sys.exit()

        inventory_id = stock_inv_model.create({'name': 'Inventory Adjustment for QOH',
                                               'location_id': location_id})
        inventory_id.prepare_inventory()

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
            print("Import successfully inventory value "
                      "for %s " % product.product_tmpl_id.name)
        print("Import successfully initial inventory value for"
              " %d products." % len(inventory_line_data))
#         inventory_id.action_done()
        print "====== END MAKE INVENTORY ADJUSTMENT ========="

from cfg_secret_configuration import odoo_configuration_user
import sys

host = odoo_configuration_user['url']
db = odoo_configuration_user['database']
user = odoo_configuration_user['login']
pwd = odoo_configuration_user['password']
input_file_path = sys.argv[1]

import_inventory_data(host, db, user, pwd, input_file_path)