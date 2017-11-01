#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
import sys
import csv
from datetime import datetime
import unicodedata as udd
from cfg_secret_configuration import odoo_configuration_user

"""
Run command:
    python 07_import_member.py imported_member.csv

To test only:
    python 07_import_member.py imported_member.csv --dry-run
"""

# ###############################################################################
# # Odoo Connection
# ###############################################################################

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

payment_method_name = "Check"
input_file = sys.argv[1]
datetime_format = "%d/%m/%Y"
datetime_str_format = "%Y-%m-%d"
share_unit_price = 10
number_of_col = 17

dry_run = False
if len(sys.argv) >= 3 and sys.argv[2] == '--dry-run':
    dry_run = True

acc_journal = openerp.AccountJournal
acc_invoice = openerp.AccountInvoice

journal_for_fundraising_ids = openerp.AccountJournal.search([('is_payment_capital_fundraising', '=', True)])
if not journal_for_fundraising_ids:
    print "=== Payment Method For fundraising not found!! Exiting"
    sys.exit()

payment_journals = openerp.AccountJournal.browse(journal_for_fundraising_ids)
ir_model_data = openerp.model('ir.model.data')
_, underclass_population_type_xml_id = ir_model_data.get_object_reference('coop_membership',
                                                                          'underclass_population_type')
print underclass_population_type_xml_id
print "payment method :\n", payment_journals
def import_member_with_subscription(is_data_validation=False):
    '''
    @Function to import member and do subscription
    '''

    payment_method = openerp.AccountJournal.search(
        [('is_payment_capital_fundraising', '=', True)], limit=1)
    if not payment_method:
        print "=== Payment Method not found!! Exiting"
        return

    payment_method = payment_method[0]

    # Read data from CSV file
    with open(input_file, 'r') as inv_file:
        f = csv.reader(
            inv_file, delimiter=',', quotechar='"')
        count = 0
        for line in f:
            if len(line) != number_of_col:
                print "Invalid Line: ", line
                continue
            count += 1
            if count == 1: # skip header
                continue
            # Member data
            id_member = int(line[0])
            sex = normalize_unicode_string_for_code(line[1]) == 'male' and 'm' or 'f'
            lastname = line[2] and encode_text(line[2]) or ''
            firstname = line[3] and encode_text(line[3]) or ''
            email = line[9] and line[9] or ''
            address = line[10] and encode_text(line[10]) or ''
            postal_code = line[11] and line[11] or ''
            city = line[12] and encode_text(line[12]) or ''
            phone = line[13] and line[13] or ''

            date_of_birth = line[14] and \
                datetime.strptime(line[14], datetime_format).date() or False
            if date_of_birth:
                date_of_birth = date_of_birth.strftime(datetime_str_format)

            # Subscription Data
            subscription_pmt = line[4]
            subscription_amt = float(line[5] or '0')
            subscription_qty = int(line[6] or '0')
            invoice_date = datetime.strptime(line[7], datetime_format).date()
            invoice_date = invoice_date.strftime(datetime_str_format)
            payment_date = datetime.strptime(line[8], datetime_format).date()
            payment_date = payment_date.strftime(datetime_str_format)
            paid_later = payment_date and invoice_date and payment_date != invoice_date
            share_category = line[16]

            # - if "no": 'confirm_payment': True
            # - if "yes": 'confirm_payment': False
#             auto_confirm = line[15] and normalize_unicode_string_for_code(encode_text(line[15])) or 'NO'
            auto_confirm = line[15] and normalize_unicode_string_for_code(encode_text(line[15])) or 'FALSE'
            if auto_confirm == 'TRUE':
                auto_confirm = True
                if paid_later:
                    auto_confirm = False
            else:
                auto_confirm = False
#             payment_method = filter(lambda x: normalize_unicode_string_for_code(x.name) == normalize_unicode_string_for_code(subscription_pmt), payment_journals)
            payment_method = acc_journal.search([('code', 'ilike', subscription_pmt.strip())])
            if not payment_method:
                print "==== Skip for ID: %d====" % id_member
                print "\t - Reason : ", payment_method, subscription_pmt
                continue
#             payment_method = payment_method[0].id
            payment_method = payment_method[0]
            # Validating data
            has_error = False

            if not subscription_amt or not subscription_qty or \
               (subscription_amt / subscription_qty) != share_unit_price:
                print "ID: %d, Share Price incorrected" % id_member
                has_error = True

            partner_name = u'%s, %s' % (lastname.strip().upper(), firstname.strip())
            if has_error:
                print "==== Skip for ID: %d - %s ====" % (id_member, partner_name)
                continue

            # Search for existing partner
            partner = openerp.ResPartner.browse(
                [('email', '=', email),
                 ('name', 'ilike', partner_name)], limit=1)
            if partner:
                partner = partner[0]
                print "Partner: %s %s existed" % (firstname, lastname)
                print "Original: ", partner.name

            if is_data_validation:
                continue
            capital_wizard_data = openerp.CapitalFundraisingWizard.default_get(
                ['payment_term_id'])
            category_id = 0
            if share_category and share_category in ['A', 'B', 'C']:
                if share_category == 'A':
                    category_id = openerp.CapitalFundraisingCategory.search([('name', 'like', 'Parts A')])
                elif share_category == 'B':
                    category_id = openerp.CapitalFundraisingCategory.search([('name', 'like', 'Parts B')])
                elif share_category == 'C':
                    category_id = openerp.CapitalFundraisingCategory.search([('name', 'like', 'Parts C')])
            if category_id == 0 or not category_id:
                print "-- Cannot find consitent category for Fundraising: %s" %  share_category
                continue
            capital_wizard_data.update({'category_id': category_id[0]})

            category_id = openerp.CapitalFundraisingCategory.browse([capital_wizard_data['category_id']])
            if not category_id:
                print "No Category existed."
                sys.exit()
            minimum_share_qty = category_id[0].minimum_share_qty
            if not partner:
                # Create a new Partner
                partner_data = {
#                     'name': u'%s ,%s' % (firstname, lastname),
                    'name': partner_name,
                    # 'barcode_base': id_member,
                    'sex': sex,
                    'email': email,
                    'street': address,
                    'zip': postal_code,
                    'city': city,
                    'phone': phone,
                    'birthdate': date_of_birth,
                }
                partner = openerp.ResPartner.create(partner_data)
            if partner and subscription_qty < minimum_share_qty:
                print "-- Partner %s has less than minimum qty shares. (%d shares) " % (partner_name, subscription_qty)

                partner.write({'fundraising_partner_type_ids': [(4, underclass_population_type_xml_id)]})

            capital_wizard_data.update({
                'date_invoice': invoice_date,
                'partner_id': partner.id,
                'share_qty': subscription_qty,
                'payment_journal_id': payment_method,
                'confirm_payment': auto_confirm
            })
            # Create Capital Subscription
            capital_sub_wizard = openerp.CapitalFundraisingWizard.create(
                capital_wizard_data)
            capital_sub_wizard.button_confirm()
            if paid_later:
                # search invoice
                inv = acc_invoice.search([('partner_id', '=', partner.id)],
                                         limit=1)
                if not inv:
                    print "Partner: %s %s cannot create invoice for Capital subcriptions." % (firstname, lastname)
                else:
                    inv = inv[0]
                    invoice = acc_invoice.browse([inv])[0]
                    payment = openerp.AccountPayment.search([('communication', '=', invoice.number),
                                                             ('state', '=', 'draft'),
                                                             ('payment_type', '=', 'inbound')])
                    if not payment:
                        print "Partner: %s %s have no payment created." % (firstname, lastname)
                    else:
                        payment = openerp.AccountPayment.browse(payment)
                        payment.write({'payment_date': payment_date})
                        try:
                            payment.post()
                        except:
                            pass

def encode_text(str_data):
    try:
        str_data = unicode(str_data, 'utf-8')
    except:
        try:
            str_data = unicode(str_data, 'iso-8859-1')
        except:
            raise Warning('File should be encoded in UTF-8!')
    return str_data

def normalize_unicode_string_for_code(str_data):
    isa_characters = u"".join([c for c in str_data if c.isalnum()])
    str_place = udd.normalize("NFKD", isa_characters).encode("ascii",
                                                             "ignore")
    return str_place.upper()


import_member_with_subscription(is_data_validation=dry_run)

