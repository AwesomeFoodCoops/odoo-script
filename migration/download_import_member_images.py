#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
import sys
import os
from cfg_secret_configuration import odoo_configuration_user
import datetime
import time
from PIL import Image
import base64
from io import BytesIO
import cStringIO
import re

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M')
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

# download with mode --download

"""
Download member image
Command :
    python download_import_member_images.py --download <folder_path>

"""
try:
    cmd = sys.argv[1]
    folder_path = sys.argv[2]
except:
    print " -- Incorrect commands."
    sys.exit()

if not os.path.isdir(folder_path):
    print "-- Folder doesn't exist."
    if cmd == '--upload':
        sys.exit()

res_partners = openerp.model('res.partner')
if cmd == '--download':
    if os.path.isdir(folder_path):
        # create folder for image
        image_path = os.path.join(folder_path, 'images', st)
        print image_path
        try:
            os.stat(image_path)
        except:
            os.mkdir(image_path)

        # get all partner then export the images
        # I just only store as binary field
        # then re-import it easily
        partner_ids = res_partners.search([('image', '!=', False)])
        if partner_ids:
            partners = res_partners.browse(partner_ids)
            for partner in partners:
                name_file = partner.name
                if not re.match("^[a-zA-Z0-9_ ,-]*$", name_file):
                    continue
                if partner.email:
                    name_file = '1 ' + name_file + " " + partner.email + ".jpeg"
                else:
                    name_file = '0 ' + name_file + ".jpeg"
                if partner.image:
                    print "Download and store image for partner : %s" % partner.name
                    file_path = os.path.join(image_path, name_file)
                    img = Image.open(BytesIO(base64.b64decode(partner.image)))
                    img.save(file_path, format="JPEG")


"""
Download member image
Command :
    python download_import_member_images.py --upload <folder_path>

file : <partner info>.jpeg
with <partner info> have to be : email or name.

"""
if cmd == '--upload':
    # get all partners
    partners = res_partners.browse([])
    partner_names = {}
    for partner in partners:
        name = partner.name.split(",")
        name = [n.strip().upper() for n in name]
        if len(name) == 2:
            data = {u" ".join([name[1], name[0]]): [partner.id, partner.name, partner.email]}
            partner_names.update(data)

    # get all files in folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            # search partner
            fn = file_name.replace('.jpeg', '').split(' ')
            partner_name = ""
            partner_email = ""
            if fn[0] == '0':
                # simpler guess the email has in
                partner_name = " ".join([st for st in fn[1:] if st.strip()])
            else:
                partner_name = " ".join([st for st in fn[1:len(fn) - 1] if st.strip()])
                partner_email = fn[-1].strip()
            domain = []
            partner_name = partner_name.upper()
            if not partner_name in partner_names:
                print "Cannot find partner %s " % partner_name
                continue
            partners = res_partners.browse([partner_names[partner_name][0]])
            print "-- Find %d partner satisfy name (%s)" % (len(partners),
                                                            partner_names[partner_name][1])
            if len(partners) > 1:
                partners = partners[0]
            img = Image.open(file_path)
            buf = cStringIO.StringIO()
            img.save(buf, format="JPEG")
            if res_partners:
                partners.write({'image': base64.b64encode(buf.getvalue())})


