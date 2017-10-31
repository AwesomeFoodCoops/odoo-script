import erppeek
import csv
import sys
import os
from cfg_secret_configuration import odoo_configuration_user


###############################################################################
# QUICK GUIDE
# Run command:
# python 97_download_stock_quant.py <output_file_path>
# Ex : python 97_download_stock_quant.py output.csv
#
# OUTPUT : file csv of qty in physical stock.
###############################################################################

output_file = sys.argv[1]


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
# SCRIPTS
###############################################################################

stock_quant_env = openerp.model('stock.quant')
stock_warehouse_env = openerp.model('stock.warehouse')
stock_location_env = openerp.model('stock.location')
product_template_env = openerp.model('product.template')
product_product_env = openerp.model('product.product')
ir_model_data_env = openerp.model('ir.model.data')

# search stock warehouse
warehouses = stock_warehouse_env.browse([])
if not warehouses:
    print "Have no warehouses. Exit!!!"
    sys.exit()
print warehouses
# search stock_quant by stock location.
product_mapped = {}
product_data = product_product_env.search_read([],
                                               ['id', 'product_tmpl_id'])
print len(product_data)
products = {}
for prd in product_data:
    if prd['id'] not in products:
        products.update({prd['id']: prd['product_tmpl_id'][0]})
print len(products)
product_template_data = ir_model_data_env.search_read([('module', 'like', '__export__'),
                                                       ('model', 'like', 'product.template')],
                                                      ['module', 'name', 'model', 'res_id'])
mapped_prd_id_prd_tmpl_ext_id = {}
vals = products.values()
for product_template in product_template_data:
    if product_template['res_id'] not in vals:
        continue
    if product_template['res_id'] not in mapped_prd_id_prd_tmpl_ext_id:
        mapped_prd_id_prd_tmpl_ext_id.update({product_template['res_id']: "%s.%s" % (product_template['module'],
                                                                                     product_template['name'])})
data = []
keys = products.keys()
def export_to_csv(file_path, data):
    with open(file_path, 'wb') as f:
        writer = csv.writer(f, delimiter=";", quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        header = ["id", "location_id/name", 'stock']
        writer.writerow(header)
        writer.writerows(data)


for warehouse in warehouses:
    location_id = warehouse.lot_stock_id.id
    print location_id
    loc_dat = stock_location_env.browse([location_id])
    if not loc_dat:
        continue
    loc_dat = loc_dat[0]
    quants = stock_quant_env.search_read([('location_id', '=', location_id)],
                                         ['product_id', 'qty'])
    product_qties = {}
    if not quants:
        continue
    for quant in quants:
        if quant['product_id'][0] not in product_qties:
            product_qties.update({quant['product_id'][0]: quant['qty']})
        else:
            product_qties[quant['product_id'][0]] += quant['qty']
    for product in product_qties.iteritems():
        dt = []
        if product[0] not in keys or \
           products[product[0]] not in mapped_prd_id_prd_tmpl_ext_id or \
           product[1] <= 0:
            continue
        print product, product[0], products[product[0]]
        dt = [mapped_prd_id_prd_tmpl_ext_id[products[product[0]]], # get external_id of product template
              loc_dat.complete_name, product[1]]
        data.append(dt)

    if not data:
        print "Cannot find Inventory %s." % loc_dat.complete_name
        sys.exit()
    head, tail = os.path.split(output_file)
    file_name = loc_dat.complete_name
    tail = file_name.replace("/", '_').replace(' ', '_') + "_" + tail
    file_path = os.path.join(head, tail)
    export_to_csv(file_path, data)
    print "-- Export succesfully file ", file_path
    data = []