#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Ticket S#13586: Urgent modification of standard point counter
    Content:
        Updating data for standard counter

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

###############################################################################
# Script
###############################################################################


def update_standard_counter():
    '''
    - Remove all Standard point counter of Present if the related member
    is of the related shift template.
    - Remove all Standard point counter of Absent and Excused if the related
    member is not of the related shift template.
    - Checking for Standard Point > 1
    '''
    to_remove_counter_ids = []
    standard_counters = openerp.ShiftCounterEvent.browse(
        [('type', '=', 'standard'),
         ('is_manual', '=', False),
         ('point_qty', '=', 1)])

    for stcounter in standard_counters:
        template_regs = stcounter.shift_id.shift_template_id.registration_ids
        for t_reg in template_regs:
            if t_reg.partner_id.id == stcounter.partner_id.id:
                to_remove_counter_ids.append(stcounter.id)
                break

    # Remove Absent and Excused
    standard_counters = openerp.ShiftCounterEvent.browse(
        [('type', '=', 'standard'),
         ('is_manual', '=', False),
         ('point_qty', 'in', [-2, -1])])

    for stcounter in standard_counters:
        template_regs = stcounter.shift_id.shift_template_id.registration_ids
        is_in_template = False
        for t_reg in template_regs:
            if t_reg.partner_id.id == stcounter.partner_id.id:
                is_in_template = True
                break
        if not is_in_template:
            to_remove_counter_ids.append(stcounter.id)

    to_remove_counter = openerp.ShiftCounterEvent.browse(to_remove_counter_ids)
    to_remove_counter.unlink()

    # Checking Points
    print "=== Partner with wrong standard counter ==="
    standard_counters = openerp.ShiftCounterEvent.browse([])
    for counter in standard_counters:
        if counter.partner_id.final_standard_point > 0:
            print counter.partner_id.name


update_standard_counter()
