#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import datetime
import time
import erppeek
import os
from os import listdir
import base64

from cfg_secret_configuration import odoo_configuration_user


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


def send_image(liste, folder_path,bool_assoc):
    no_picture = 0
    picture = 0
    print "number of objects in folder path : ", len(listdir(folder_path))
    count = 0
    for m in liste :
            file_path = folder_path+str(m.barcode_base)+".JPG"
            if bool_assoc :
                file_path = folder_path+str(m.parent_id.barcode_base)+".JPG"
            print file_path, m.name
            if os.path.isfile(file_path):
                with open(file_path, "rb") as image_file:
                    content = image_file.read()
                    encoded_string = base64.b64encode(content)
                    m.write({'image' : encoded_string})
                    print '   => photo enregistrée'
                    picture=picture+1
            else:
                no_picture = no_picture+1
                print "    => pas de photo"
            count=count+1
            print count

    print "avec photo", picture
    print "sans photo", no_picture

associated_people_ids = openerp.search('res.partner', [('is_associated_people', '=', True), ('barcode_base', '!=', False)])
members_ids = openerp.search('res.partner', [('is_associated_people', '=', False), ('barcode_base', '!=', False)])

associated_people = openerp.ResPartner.browse([('id', 'in', associated_people_ids)])
members = openerp.ResPartner.browse([('id', 'in', members_ids)])

print ">>>>>>>> Number of members people found: ", len(members)
send_image(members, "/home/louve-erp-prod/photos/cooperateurs/", False)

print ">>>>>>>> Number of associated people found: ", len(associated_people)
send_image(associated_people, "/home/louve-erp-prod/photos/rattaches/", True)
