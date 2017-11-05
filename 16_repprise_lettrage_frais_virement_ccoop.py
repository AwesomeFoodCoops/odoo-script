#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
import sys
#from config_prod import odoo_configuration_user
from config_test import odoo_configuration_user
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

id_journal_LCR = 103
id_compte_comptable_LCR = 265 #403000 - Fournisseurs - Effets à payer 

mode_test = False

def delta_day(date,force_delay=None):
    date_1 = datetime.datetime.strptime(date, "%Y-%m-%d")
    if force_delay==None :
        delay_day = 1
        if (date_1.weekday() == 5):
            delay_day = 2
    else :
            delay_day = force_delay
    end_date = date_1 + datetime.timedelta(days=delay_day)
    res = end_date.strftime('%Y-%m-%d')
    print "date session : ", date
    print "delay_day : ",delay_day 
    print "date max : ", res
    return res


def already_reconcilled(move_lines):
    for move_line in move_lines :
        if move_line.reconciled:
	    return True
    return False

def reconcile_frais_bancaires(id_journal_compte_bancaire,id_compte_comptable_frais_bancaires,date_debut, date_fin, id_ligne_releve_banque=None):
    i = 0
    print ">>>>>>> START UPDATING >>>>>>>>>>"

    if id_ligne_releve_banque==None:
        lignes_frais_virement = openerp.AccountBankStatementLine.browse([('name', 'like', "COMMISSION VIR SEPA EMIS"), ('journal_entry_ids','=',False),('date', '>=', date_debut),('date', '<=', date_fin),('journal_id', '=', id_journal_compte_bancaire)],order='date')
    else :
        lignes_frais_virement = openerp.AccountBankStatementLine.browse([('id', '=',id_ligne_releve_banque),('journal_entry_ids','=',False)])

    print "Nombre de lignes",len(lignes_frais_virement)
    print "     > Rapporchement direct frais bancaires sans apairage avec les télecollectes"

    for line in lignes_frais_virement:
        i = i+1
        print "==============================="
        print " Avancement : ",i, "/",len(lignes_frais_virement)
        print "==============================="
        print "         name",line.name
        print "         note",line.note
        print "         amount",line.amount
        print "         date",line.date

        move_line_data_credit = {
            'name': 'Frais virement SEPA',
            'debit': line.amount * -1,
            'credit': 0.0,
            'journal_id': id_journal_compte_bancaire,
            'date': line.date,
            'account_id': id_compte_comptable_frais_bancaires,
        }
        print "         -> ligne de banque générée : ", move_line_data_credit
        if mode_test == False :
            print line.process_reconciliation_wrapper([move_line_data_credit])

################################

id_compte_comptable_frais_bancaires = 502  # 627100  - Frais bancaires CCOOP

date_debut = '2017-01-01'
date_fin = '2017-09-29'

#print "############### Transaction LCR sur CEP compte courant"
#id_journal_CEP = 49
#reconcile_lcr(id_journal_CEP,id_compte_comptable_CEP,date_debut,date_fin)

print "############### Transaction LCR sur Ccoop compte courant"
id_journal_Ccoop = 46
reconcile_frais_bancaires(id_journal_Ccoop,id_compte_comptable_frais_bancaires,date_debut,date_fin)

#reconcile_frais_bancaires(id_journal_CEP,id_compte_comptable_frais_bancaires,None,None,id)

print "\n>>>>>>> DONE >>>>>>>>>>"
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")
