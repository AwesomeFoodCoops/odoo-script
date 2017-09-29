#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Ticket S#13625: Fix status for replacing attendees
    Content:
    - Update all replacing attendance to `replacing`

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


def update_replacing_attendance():
    '''
    @Function to correct the replacing attendance
    '''
    replaced_attendances = openerp.ShiftRegistration.browse(
        [('state', '=', 'replaced')])

    print "%d replaced attendances found" % len(replaced_attendances)

    for replace_att in replaced_attendances:
        if not replace_att.replacing_reg_id:
            print "Replaced Attendance with no replacing: ", replace_att.id
            continue

        if replace_att.replacing_reg_id.state != 'replacing':
            replace_att.replacing_reg_id.state = 'replacing'
            replace_att.replacing_reg_id.template_created = False
    print "========= Update Done ============"


update_replacing_attendance()
