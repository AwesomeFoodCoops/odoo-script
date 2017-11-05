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

mode_test = True
date_debut = '2017-01-01'
date_fin = '2017-09-29'

id_journal_CCOOP = 46
journal_CB_souscription = 75 
account_souscription_CB = 810 # 511510 - Carte Bleue SOUSCRIPTIONS 

lignes_CB = openerp.AccountBankStatementLine.browse([('name','like','5138325 REM%'),('journal_entry_ids','=',False),('date', '>=', date_debut),('date', '<=', date_fin),('journal_id', '=', id_journal_CCOOP)],order='date')


i=0
ko=0
for ligne in lignes_CB:
    i+=1
    print "========= Avancement : ",i,"/",len(lignes_CB)
    print "    => ko =",ko
    print "         > ",ligne.name,ligne.date
    ligne_telecollecte = re.compile(u"^5138325 REM (?P<telecollecte>\d{6}) DU (?P<date>\d{6}): SAS COOPERATIVE LA LOUVE$").search(ligne.name)
    date_str = ligne_telecollecte.group('date')
    telecollecte = ligne_telecollecte.group('telecollecte')
    date_format_odoo = datetime.datetime.strptime(date_str, "%d%m%y").strftime('%Y-%m-%d')
    ecriture_journal_paiement_CB_souscription = openerp.AccountMoveLine.browse([('journal_id','=',journal_CB_souscription),('date','=',date_format_odoo),('account_id','=',account_souscription_CB),('full_reconcile_id','=',False)])
    print "Nombre de lignes pour ce jour", len(ecriture_journal_paiement_CB_souscription)
    montant_total = 0.0
    liste_ecritures = []
    for li in ecriture_journal_paiement_CB_souscription:
        print "             -> ",li.name, li.date, li.debit
        montant_total += li.debit
        liste_ecritures.append(li.id)

    if montant_total != ligne.amount:
        print "Le montant total des paiements souscription CB du jour de télécollecte n'est pas égal au montant figurant sur ce relevé"
        ko = ko+1
        print  montant_total, abs(ligne.amount)
    else :
        # Rapprocher et générer l'écriture de banque
        move_line_contact = {
                'name': 'Télecollecte souscription '+ligne.date+' '+ligne.name,
                'debit': 0.0,
                'credit': abs(ligne.amount),
                'journal_id': id_journal_CCOOP,
                'date': ligne.date,
                'account_id': account_souscription_CB,
                }
        print move_line_contact

        if mode_test == False :
            print "     > Création de l'écriture de branque et rapprochement"
            res = bank_line.process_reconciliation_wrapper([move_line_contact])

            #Lettrer
            for move_line in ligne.journal_entry_ids[0].line_ids:
                if move_line.account_id.id == account_id_credit and move_line.id not in liste_ecritures:
                    liste_ecritures.append(move_line.id)
            wizard_id = 1
            print "Lettrage des écritures : ",liste_ecritures
            r = openerp.execute_kw('account.move.line.reconcile', 'trans_rec_reconcile_full', [wizard_id], {'context': {'active_ids': liste_ecritures}})
            print r
#    exit(0)


print "\n>>>>>>> DONE >>>>>>>>>>"
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")
