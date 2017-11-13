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

id_compte_capital_appele_non_verse = 3 #101200 - Parts A - KSANV

mode_test = True

def lettrage_capilat_nonerse_verse(move_line_id=None):
    print ">>>>>>> START UPDATING >>>>>>>>>>"

    ecritures_remboursement_capital = openerp.AccountMoveLine.browse([('name','=',"Remboursement de capital"),('account_id','=',id_compte_capital_appele_non_verse)])
    partner_ecriture_rem_cap = ecritures_remboursement_capital.id
    print partner_ecriture_rem_cap


    if (move_line_id==None):
        a_lettrer = openerp.AccountMoveLine.browse([('name','!=',"Remboursement de capital"),('account_id','=',id_compte_capital_appele_non_verse),('full_reconcile_id','=',False),('debit','=',0.0),('credit','!=',0.0)],order='id')
    else : 
        a_lettrer = openerp.AccountMoveLine.browse([('id','=',move_line_id)],order='id')

    i = 0
    ok=0
    aucune_facture=0
    facture_non_payee=0
    debit_different_credit=0
    exclusion_remb_cap=0
    pieces_debit_different_credit=[]
    for ecriture_credit in a_lettrer:
        print "==============================="
        print " Avancement : ",i, "/",len(a_lettrer)
        print "          aucune_facture",aucune_facture
        print "          facture_non_payee",facture_non_payee
        print "          exclusion_remb_cap",exclusion_remb_cap
        print "          debit_different_credit",debit_different_credit
        print "          ok",ok
        print "==============================="
        print "         libelle de l'écriture",ecriture_credit.name
        print "         ID de l'écriture",ecriture_credit.id
        print "         nom de la piece de rattachement",ecriture_credit.move_id.name
        print "         credit",ecriture_credit.credit
        print "         debit",ecriture_credit.debit
        print "         partner_id",ecriture_credit.partner_id.id, "num coop", ecriture_credit.partner_id.barcode_base
        print "         date",ecriture_credit.date
        i = i+1

        factures = openerp.AccountInvoice.browse([('move_id','=',ecriture_credit.move_id.id)])

        if len(factures) != 1 :
            aucune_facture +=1
            print "         Impossible trouver facture"
            continue

        facture = factures[0]
        print "         Facture",facture.number

        if facture.state != 'paid':
            facture_non_payee += 1
            print "                  => La facture n'est pas à l'état payé"
            continue
        
        if facture.partner_id.id in partner_ecriture_rem_cap:
            exclusion_remb_cap += 1
            print "                 => Ce partner est lié à des écriture 'Remboursement de capital'"
            continue

        line_to_reconcil = [ecriture_credit.id]
        total_credit = ecriture_credit.credit
        total_debit = 0.0
        

        ecritures_debit = openerp.AccountMoveLine.browse([('name','!=',"Remboursement de capital"),('account_id','=',id_compte_capital_appele_non_verse),('full_reconcile_id','=',False),('credit','=',0.0),('debit','!=',0.0),('ref','=',ecriture_credit.move_id.name),('partner_id','=',facture.partner_id.id)])

        for ecriture_debit in ecritures_debit:
            print "             Ajout ligne ID",ecriture_debit.id," / Libelle", ecriture_debit.name," / debit=",ecriture_debit.debit, "/ credit=",ecriture_debit.credit
            total_debit+=ecriture_debit.debit
            line_to_reconcil.append(ecriture_debit.id)

        if (abs(total_credit-total_debit))>0.000001:
                print "          Total des debit et credit différents"
                print "             Total credit",total_credit
                print "             Total debit",total_debit
                debit_different_credit += 1
                pieces_debit_different_credit.append(ecriture_credit.move_id.id)
                print "             => liste des picèes KO credit different debit",pieces_debit_different_credit
                continue

        print line_to_reconcil
        print "ok"
        ok += 1
        if (mode_test == False) : 
            wizard_id = 1
            r = openerp.execute_kw('account.move.line.reconcile', 'trans_rec_reconcile_full', [wizard_id], {'context': {'active_ids': line_to_reconcil}})
            print r

    print "================================"
    print "             => liste des picèes KO credit different debit",pieces_debit_different_credit
    print "             => liste des partenr KO car liés à une écriture remboursement de capital",partner_ecriture_rem_cap
################################


lettrage_capilat_nonerse_verse(469241)
#lettrage_capilat_nonerse_verse()

print "\n>>>>>>> DONE >>>>>>>>>>"
print datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%s")
