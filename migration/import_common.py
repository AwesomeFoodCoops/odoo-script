#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @author Nils Hamerlinck
# @author TienDV

import codecs, sys
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import random
import requests
import simplejson
import csv
import re

DRY_RUN = False
COMPAT = True
REMOVE = ['image_small', 'image', 'image_medium',]

###
# AUTHENTICATE
###
def authenticate_xmlrpc(host, db, user, pwd):
    if host and db and user and pwd:
        return requests.post('%s/web/session/authenticate' % host,
                             json={ "jsonrpc": "2.0",
                                    "method":"call",
                                    "params":{  'db': db,
                                                'login': user,
                                                'password': pwd },
                                   "id": random.randint(0, 1000000000) })

def get_result(reqs):
    return simplejson.loads(reqs.text)["result"]

##
# CREATE IMPORT
##
def request_import_via_csv(host, reqs, db, model, input_file):
    import os.path
    if not os.path.isfile(input_file):
        print "-- File doesn't exist."
        return
    print "-- File existed, try to import."
    # open import form.
    crsf_token = renew_crsf_token(host, db, reqs)

    reqs = requests.post('%s/web/dataset/call_kw' % host,
                         json={"params":{"model":"base_import.import",
                                         "method":"create",
                                         "args":[{"res_model":model}],
                                         "kwargs":{}},
                               "jsonrpc": "2.0",
                               "method": "call",
                               "id": random.randint(0, 1000000000)},
                         headers={ "Content-Type": "application/json"},
                         cookies=reqs.cookies)
    import_id = int(simplejson.loads(reqs.text)["result"])
    # handle when error
    # need to be return false
    if 'error' in reqs.text:
        return
    print "-- Finish get crsf_token and go to import page."
    print crsf_token
    # push file
    reqs = requests.post('%s/base_import/set_file?csrf_token=%s' % (host,
                                                                    crsf_token),
                          data={'import_id': import_id},
                          files={'file': codecs.open(input_file, 'r', 'utf-8')},
                          cookies=reqs.cookies,)
    print "\n\n ", reqs.text
    if 'error' not in reqs.text:
        print "-- Reviewing format of file and test importing."
        # preview import
        revw = requests.post('%s/web/dataset/call_kw' % host,
                             json={"params":{"model":"base_import.import",
                                             "method":"parse_preview",
                                             "args":[ import_id,
                                                     {"headers": True,
                                                      "encoding": "utf-8",
                                                      "separator": ",",
                                                      "quoting": '"'}],
                                             "kwargs":{}},
                                   "jsonrpc": "2.0",
                                   "method": "call",
                                   "id": random.randint(0, 1000000000)},
                             headers={ "Content-Type": "application/json"},
                             cookies=reqs.cookies)
        try:
            preview = simplejson.loads(revw.text)["result"] # ["preview"]
            # try to import
            _, fields = get_list_fields(input_file, preview['headers'])
            no_relation_hd = []
            if 'parent_id/id' in fields or \
                'child_ids/id' in fields or \
                'child_id/id' in fields:
                # try to import no-relation data
                for h in fields:
                    if h == 'id':
                        no_relation_hd.append(h)
                        continue
                    if h in ['parent_id/id', 'child_ids/id', 'child_id/id']:
                        no_relation_hd.append(False)
                    else:
                        no_relation_hd.append(h)
        except:
            print revw.text
            return
        print "-- Try to import after tests."
        if no_relation_hd:
            print "Install 2 steps"
            reqs = requests.post('%s/web/dataset/call_kw' % host,
                             json={"params":{"model":"base_import.import",
                                             "method":"do",
                                             "args":[import_id,
                                                     no_relation_hd,
                                                     {"headers": True,
                                                      "encoding": "utf-8",
                                                      "separator": ",",
                                                      "quoting": '"'}],
                                             "kwargs":{'dryrun':DRY_RUN,
                                                       'context':{}}},
                                   "jsonrpc": "2.0", "method": "call",
                                   "id": random.randint(0, 1000000000)},
                             headers={ "Content-Type": "application/json"},
                             cookies=reqs.cookies)
        reqs = requests.post('%s/web/dataset/call_kw' % host,
                             json={"params":{"model":"base_import.import",
                                             "method":"do",
                                             "args":[ import_id, fields,
                                                     {"headers": True,
                                                      "encoding": "utf-8",
                                                      "separator": ",",
                                                      "quoting": '"'}],
                                             "kwargs":{'dryrun':DRY_RUN,
                                                       'context':{}}},
                                   "jsonrpc": "2.0", "method": "call",
                                   "id": random.randint(0, 1000000000)},
                             headers={ "Content-Type": "application/json"},
                             cookies=reqs.cookies)
        try:
            preview = simplejson.loads(reqs.text)["result"] # ["preview"]
            if len(preview) == 0:
                print "-- IMPORT SUCCESSFULLY !"
            else:
                for msg in preview:
                    print msg['rows'], msg['message']
        except:
            print "-- IMPORT ERROR"
            print reqs.text
        return

def get_list_fields(input_file, input_header=False):
    f = csv.reader(codecs.open(input_file, 'r', 'utf-8'),
                   delimiter=',',
                   quotechar='"')
    header = f.next()
#     fields = map(eval, header)
    if input_header:
        input_header = [str(t) for t in input_header]
        fields = map(lambda x: (x in input_header) and x, header)
        fields = [x for x in fields if x]
    else:
        fields = header
    for f in REMOVE:
        if f in fields:
            fields.remove(f)
    return header, fields

def renew_crsf_token(host, db, reqs):
    r = requests.get(host + '/web?db=%s' % db,
                     cookies=reqs.cookies)
    m = re.compile(r'token = "(?P<csrf_token>[^"]+)"').search(r.text)
    csrf_token = m.group('csrf_token')
    return csrf_token
