#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Content:
    - Get and validate Email Address of Partner.
    - Command :
    python 11_validate_email_address.py <file_path>
      - file_path : where to saving file result. E.g. : /opt/example/result.csv
    Example:
    python 11_validate_email_address.py /opt/example/result.csv

'''
from cfg_secret_configuration import odoo_configuration_user
import erppeek
import sys
import re
import csv
import xmlrpclib

try:
    from validate_email import validate_email
    from DNS import TimeoutError
except ImportError:
    validate_email = None
    print "Cannot find validate_email installed in your system."
    print "Please run below scripts and try to run script again."
    print "pip install validate_email"
    print "pip install pyDNS"
    sys.exit()

if not sys.argv[1]:
    print "Lost file path"
    sys.exit()
output_file_path = sys.argv[1]


###############################################################################
# Odoo Connection
###############################################################################

# matches a string containing only one email
single_email_re = re.compile(r"""^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$""", re.VERBOSE)

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

MAPPING_RESULT = {0: [0, "Good !"],
                  1: [1, "Bad Syntax !"],
                  2: [2, "Email doesn't exist."],
                  3: [3, "Check MX failed."]}

def validate_email_with_mx(email, check_mx=True):
    '''
    @Function to validate an email address, return :
      - 0 : this email existed
      - 1 : this email has wrong syntax.
      - 2 : this email domain can not be verified.
      - 3 : this email has correct syntax but can not be verified successfully.
    '''
    if single_email_re.match(email):
        try:
            is_valid = validate_email(email, check_mx=True, verify=True)
            if is_valid:
#                 print("%s Valid!" % email)
                return 0
            elif is_valid is None:
#                 print("I'm not sure. - %s" % email)
                return 3
            else:
#                 print "Invalid mail server : ", email
                return 2
        except TimeoutError:
#             print("TimeoutError - %s" % email)
            return 3
    else:
#         print "Invalid format address : ", email
        return 1

def get_and_validate_email_addresses():
    '''
    @Function to get all email addresses from user and partner.
    '''
    # validate for partner
    partners = openerp.ResPartner.browse([])
    invalid_emails = []
    correct_emails = []
    print "==== Check %d Partner =======" % len(partners)
    count = 0
    for partner in partners:
        count += 1
        print "--- Checked %d/%d - %s" % (count, len(partners), partner.email)
        # pass if partner doesn't have email.
        if not partner.email:
            continue
        record = [partner.id, partner.barcode_base, partner.name,
                  partner.email]
        # if in email address string has white space
        # list in invalid email
        if ' ' in partner.email:
            record += MAPPING_RESULT[1]
            record[-1] = "String has white space."
            invalid_emails.append(record)
        else:
            try:
                # call model function to assure that it's consistent
                # this can be replace by above function for other purpose.
                openerp.ResPartner.validate_email_address(partner.email)
                record += MAPPING_RESULT[0]
                correct_emails.append(record)
            except xmlrpclib.Fault as err:
                record += MAPPING_RESULT[2]
                record[-1] = "%s" % err.faultCode.__str__()
                invalid_emails.append(record)
        print "--- Checked %d/%d - %s - %s" % (count, len(partners),
                                               partner.email,
                                               record[-1])
    return invalid_emails, correct_emails

def parse_to_csv(file_name, header, data):
    print "-- Start writing for file : ", file_name
    with open(file_name, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        # write header
        spamwriter.writerow(header)
        for dt in data:
            dt = [isinstance(d, (str,unicode)) and d.encode('utf-8')
                  or d for d in dt]
            spamwriter.writerow(dt)
    print "-- Successfully writing for %d records to file : %s" % (len(data),
                                                                   file_name)

# Collect and list all emails addresses.
invalid_emails, correct_emails = get_and_validate_email_addresses()
header = ['id', 'barcode_base', 'name', 'email', 'reason_code', 'reason']
if invalid_emails:
    parse_to_csv(output_file_path, header, invalid_emails)
print "=== END. Goodbye !"