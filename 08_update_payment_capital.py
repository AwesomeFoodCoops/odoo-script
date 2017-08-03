#! /usr/bin/env python
# -*- encoding: utf-8 -*-

'''
    Correction paiements sur facture de capital/souscription importés que partiellement depuis CiviCRM pour les membres échelonnés n'ayant pas encore tout payé
'''
import erppeek
import sys
from config_test import odoo_configuration_user

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


def correct_capital_payement():
    targeted_invoice_ids = ['16SCPT00006118','16SCPT00006117','16SCPT00006116','16SCPT00006113','16SCPT00006112','16SCPT00006102','16SCPT00006097','16SCPT00006096','16SCPT00006095','16SCPT00006094','16SCPT00006089','16SCPT00001037','16SCPT00006080','16SCPT00006079','16SCPT00006070','16SCPT00006069','16SCPT00006068','16SCPT00006043','16SCPT00006030','16SCPT00006027','16SCPT00006020','16SCPT00006005','16SCPT00006000','16SCPT00005990','16SCPT00005983','16SCPT00005976','16SCPT00005975','16SCPT00005968','16SCPT00005965','16SCPT00004663','16SCPT00003698','16SCPT00005930','16SCPT00005927','16SCPT00005916','16SCPT00005907','16SCPT00005904','16SCPT00005897','16SCPT00005888','16SCPT00005887','16SCPT00005846','16SCPT00005845','16SCPT00003674','16SCPT00005836','16SCPT00005833','16SCPT00005832','16SCPT00005831','16SCPT00005830','16SCPT00005811','16SCPT00005808','16SCPT00005807','16SCPT00005800','16SCPT00005793','16SCPT00005790','16SCPT00005785','16SCPT00005765','16SCPT00005764','16SCPT00005755','16SCPT00005754','16SCPT00005751','16SCPT00005734','16SCPT00005733','16SCPT00005730','16SCPT00004696','16SCPT00005729','16SCPT00005728','16SCPT00005723','16SCPT00005716','16SCPT00005695','16SCPT00005694','16SCPT00004311','16SCPT00003713','16SCPT00005661','16SCPT00005652','16SCPT00003691','16SCPT00005573','16SCPT00005557','16SCPT00005554','16SCPT00005546','16SCPT00005513','16SCPT00005506','16SCPT00005496','16SCPT00005474','16SCPT00005404','16SCPT00005396','16SCPT00005327','16SCPT00005280','16SCPT00005334','16SCPT00005231','16SCPT00005149','16SCPT00005076','16SCPT00005009','16SCPT00005008','16SCPT00004638','16SCPT00004523','16SCPT00004522']

    print ">>>>>>> START UPDATING >>>>>>>>>>"
    print targeted_invoice_ids
    invoices = openerp.AccountInvoice.browse([('number', 'in', targeted_invoice_ids)])
    #id_journal_cheque_souscription = 77

    for invoice in invoices:
        print "===========================================", invoice.number, invoice.partner_id
        #payment_cap_member = openerp.AccountPayment.browse([('partner_id','=',invoice.partner_id.id),('journal_id','=',id_journal_cheque_souscription)])
        payment_cap_member = openerp.AccountPayment.browse([('partner_id','=',invoice.partner_id.id)])

        total_payments = 0.0
        for payment in payment_cap_member :
            #print payment.amount
            total_payments += payment.amount

        if (total_payments != invoice.amount_total):
            print "La somme totale des montants des paiements ouverts ne correspond pas à la facture de capital ouverte : ", invoice.amount_total
            continue

        for payment in payment_cap_member :
            print "       >>>> ", payment, payment.partner_id

            ####### VERIFIER QU'ON NE MODIFIE PAS UN PAIMENT BON !
            #print "       ", "Nb factures liées", len(payment.invoice_ids)
            if (len(payment.invoice_ids)>0):
                print "       ", "Factures présentes, ne pas délettrer ce paiement."
                if (payment.state == 'draft'):
                    print "       ", "Ce paiement a simplement été confirmé."
                    try:
                        payment.post()
                    except Exception:
                        pass
                continue

            # ANNULER LE LETTRAGE DE TOUTES LES ECRITURES DU PAIEMENT
            for ecriture in payment.move_line_ids :
                print "              >>>> ",ecriture
                if (ecriture.reconciled):
                    ecriture.remove_move_reconcile()
                    print "              ","==> Annulation du lettrage"

            # ANNULER LE PAIEMENT
            if (payment.state != "draft"):
                print "       ","Annulation du paiement : "
                try:
                    payment.cancel()
                except Exception:
                    pass

            # MODIFIER LE PAIEMENT POUR LUI METTRE LE NUMERO DE LA FACTURE
            payment.invoice_ids = [invoice.id]
            print "       ","Enregistrement de la facture sur le paiement"

            #CONFIRMER LE PAIEMENT
            try:
                payment.post()
            except Exception:
                pass
            print "       ","Validation du paiement"

correct_capital_payement()
print "\n>>>>>>> DONE >>>>>>>>>>"
