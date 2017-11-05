#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
import sys
from config_prod import odoo_configuration_user
#from config_test import odoo_configuration_user
import datetime
import re

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

##################################################################
##########                  SET LOGGER                  ##########
##################################################################
class Logger(object):
    def __init__(self, filename='Default.log'):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

log_file = 'log_' + datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")+'.log'
print "stdout = ./"+log_file
sys.stdout = Logger(log_file)
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")

###############################################################################
# Script
###############################################################################

date_debut = '2017-01-01'
date_fin = '2017-09-29'

id_journal_CEP = 49

lignes_frais_virement = openerp.AccountBankStatementLine.browse([('journal_entry_ids','=',False),('date', '>=', date_debut),('date', '<=', date_fin),('journal_id', '=', id_journal_CEP)],order='date')

i=0
for ligne in lignes_frais_virement:
    i=i+1
    print "Avancement : ",i,"/",len(lignes_frais_virement)
    ligne.partner_id = False
    ligne.name = ligne.name + " */* " + ligne.note
    ligne.note = False
#    print ligne.partner_name

print "\n>>>>>>> DONE >>>>>>>>>>"
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")
