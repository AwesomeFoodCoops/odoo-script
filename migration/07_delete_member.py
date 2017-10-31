#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
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

# Find all member without associated people
res_partner_model = openerp.model('res.partner')
acc_invoice_model = openerp.model('account.invoice')
acc_move_model = openerp.model('account.move')
acc_move_line_model = openerp.model('account.move.line')
acc_payment_model = openerp.model('account.payment')
ir_sequences_model = openerp.model('ir.sequence')
owner_shares_model = openerp.model('res.partner.owned.share')

def delete_members():
    # search all member
    members = res_partner_model.search([('is_member', '=', True)])
    if members:
        for member in members:
            print "----- DELETE MEMBER %s -------" % member
            delete_one_member(member)
    # reset sequence
    names = [u'Capital', u'CHEQUES REÇUS', u'Customer Invoices',
             u'Sequence - Numeration of Coop Member', u'Account reconcile sequence']
    seq_ids = ir_sequences_model.search([('name', 'in', names)])
    if seq_ids:
        print "-- Update sequences : ", seq_ids
        ir_sequences_model.browse(seq_ids).write({'number_next_actual': 1})


def delete_one_member(member_id):
    member = res_partner_model.browse([member_id])
    member = member and member[0]
    if member:
        # search involving payment
        domain = [('type','in', ['out_invoice', 'out_refund']),
                  ('state', 'not in', ['draft', 'cancel']),
                  ('partner_id', '=', member_id),
                  ('number', 'like', 'CAP/%')]
        invoices = acc_invoice_model.search(domain)
        if not invoices:
            print "-- Cannot find invoices for %s " % member.name
            return
        inv_4_del = []
        am_4_del = []
        aml_4_del = []
        pmt_4_del = []
        # delete owner shares
        owner_shares = owner_shares_model.search([('partner_id', '=', member_id)])
        owner_shares = owner_shares and owner_shares_model.browse(owner_shares)[0] or []
        if owner_shares:
            print "-- Delete %s owner_shares." % owner_shares.name
            owner_shares.unlink()

        for inv in acc_invoice_model.browse(invoices):
            move_id = inv.move_id
            name = move_id.name
            moves = acc_move_model.search(['|', ('name', '=', name),
                                           ('ref', '=', name)])
#             print moves
            # unreconcile payment first
            lines = []
            for mv in acc_move_model.browse(moves):
                aml_4_del += list(line.id for line in mv.line_ids)
                am_4_del.append(mv.id)
                lines += [l.id for l in mv.line_ids]
            acc_move_line_model.browse(lines).remove_move_reconcile()

            # after remove reconcile new account move create for refund
            refund_mvs = acc_move_model.search(['|', ('name', '=', name),
                                                    ('ref', '=', name)])
            for rfm_id in refund_mvs:
                if rfm_id not in aml_4_del:
                    am_4_del.append(rfm_id)
                    rfn_mv = acc_move_model.browse(rfm_id)
                    aml_4_del += list(line.id for line in rfn_mv.line_ids)
                    rfn_mv.line_ids.remove_move_reconcile()

            # cancel invoice which is in open state
            if inv.state == 'open':
                inv_4_del.append(inv.id)
            # cancel payment
            pmt_id = acc_payment_model.search([('communication', '=', name)])
            if pmt_id:
                print "-- Delete  payment ID %s " % str(pmt_id)
                payments = acc_payment_model.browse(pmt_id)
                if payments:
                    for pm in payments:
                        aml_4_del += list(line.id for line in pm.move_line_ids)
                        cancel_payment(pm)
                pmt_4_del += pmt_id

        ams = am_4_del and acc_move_model.browse(am_4_del)
        ams.button_cancel()
        # delete invoice
        invs = inv_4_del and acc_invoice_model.browse(inv_4_del)
        if invs:
            print "-- Delete %d invoice." % len(invs)
            invs.action_cancel()
            invs.write({'move_name': False})
            if pmt_4_del:
                acc_payment_model.browse(pmt_4_del).unlink()
        if ams:
            print "-- Delete %d account move." % len(ams)
            for am in ams:
                if am and acc_move_model.search([('id', '=', am.id)]):
                    am.unlink()
        amls = aml_4_del and acc_move_line_model.browse(aml_4_del)
        if amls:
            print "-- Delete %d account move line." % len(amls)
            for aml in amls:
                if aml and acc_move_line_model.search([('id', '=', aml.id)]):
                    aml.unlink()
        invs.action_cancel()
        invs.write({'move_name': False})
        invs.unlink()
    try:
        print "-- Delete member"
        member.unlink()
    except:
        print "-- Cannot unlink member %s" % member.name


def cancel_payment(pmt):
    moves = []
    for ml in pmt.move_line_ids:
        if ml.move_id not in moves:
            moves.append(ml.move_id)
    ids = [move.id for move in moves if move]
    ids = ids and acc_move_model.search([('id', 'in', ids)])
    moves = acc_move_model.browse(ids)
    print moves
    for move in moves:
        if pmt.invoice_ids:
            if move.line_ids:
                move.line_ids.remove_move_reconcile()
        move.button_cancel()
    pmt.state = 'draft'

delete_members()





