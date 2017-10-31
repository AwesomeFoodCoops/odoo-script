
import gspread
import sys
from oauth2client.service_account import ServiceAccountCredentials
import os
import csv
from import_common import authenticate_xmlrpc, request_import_via_csv
from cfg_secret_configuration import odoo_configuration_user, MAX_ROW_FOR_FILE, \
    data_links, data_csv_name, credentials_path, DEDICATED_LST
import simplejson

dir_path = os.path.dirname(os.path.realpath(__file__))


"""
Command install:
    pip install gspread oauth2client

Command to run:
    python connect_and_download_spreadsheet.py <name of sheets>
    Example : python connect_and_download_spreadsheet.py COA
    Example : python connect_and_download_spreadsheet.py Users COA Journals

Note that:
    - For member.csv, we have specific format that it's not fit with native
    import format, so the script will stop at download member.csv
    - For some sheet that it have more lines than MAX_ROW_FOR_FILE, the script
    will split this sheet to many files then import them.
    - When running script, the login account have to be set expected Language.
    - To avoid print all Logs on screen can use `&> log.txt` to print all logs
    into file txt.
        Example : python connect_and_download_spreadsheet.py COA &> log.txt
"""

# make the scope generic with drive file
scope = ['https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']


# link to file of Service Account Credential (JSON file downloaded after register service credentials)
# Note that: each service account have an email that the document have to be shared with this email.
# credentials = ServiceAccountCredentials.from_json_keyfile_name('/opt/openerp/code/project/projects/lalouve_projects/My Project-8844cb4f5e41.json', scope)
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

gc = gspread.authorize(credentials)
print "-- Login success with to gsheet. Start getting data."
try:
    wks = gc.open_by_url(data_links)
    print wks
except:
    # this case that it means permission denied or sheet doesn't exist.
    print " -- INVALID DATA file. Exit!!!"
    sys.exit()

# get list from Params
sheets = []
if len(sys.argv) >= 2:
    for a in sys.argv:
        if a in data_csv_name:
            sheets.append(a)
            print "- Prepare for import sheet : %s" % a
if not sheets:
    print "Nothing to do. Exit!!!"
    sys.exit()

# create folder to saving csv
data_path = os.path.join(dir_path, 'data')
try:
    os.stat(data_path)
except:
    os.mkdir(data_path)

# delete old files in folder
# I will update code for backup data file later.
# import shutil
for root, dirs, files in os.walk(data_path):
    for f in files:
        os.unlink(os.path.join(root, f))

list_file = []
for sheet in sheets:
    print "- Download sheet : %s" % sheet
    split = False
    sh = wks.worksheet(sheet)
    if sh:
        file_path = os.path.join(data_path, data_csv_name[sheet][0])
        list_file.append((data_csv_name[sheet][1], file_path))
        with open(file_path, 'wb') as f:
            buf = sh.export()
            f.write(buf)
        print "\t- Download successfully, file : %s" % file_path

if not list_file:
    print "No file to be download. Exit !!!"
    sys.exit()

# process downloaded file
# for each csv do:
# 1. Find row which has first cell is `Columns` to get the headers
# 2. Find row which has first cell is `Command` to get the deliminated columns.
# 3. Find row which has first cell is `Your values` to get data bases on header.
# 4. Save to file csv. If more than 500 rows in file, split it before saving.
def open_csv_and_reformat_file(file_path):
    if not os.path.isfile(file_path):
        print "\t- File not exists : ", file_path
        return None
    print "\t- Open file : ", file_path
    header = []
    command = []
    values = []
    # get values
    with open(file_path, 'rb') as f:
        reader = csv.reader(f)
        val = False
        for line in reader:
            if line[0] == 'Columns':
                header = line[1:]
            elif line[0] == 'Command':
                command = [idx if l != "(don't import)" else False
                           for idx, l in enumerate(line[1:])]
            elif line[0] == 'Your values':
                val = True
                values.append(line[1:])
            elif val:
                values.append(line[1:])
    if not header or not values:
        print "\t- Cannot find header or values is empty: ", file_path
        print "\tFind header : ", header
        print "\tFind values : ", len(values)
        return None
    if command:
        print "\t- Filter columns: ", command
        header = [header[idx] for idx in command if idx is not False]
        new_values = []
        for line in values:
            new_values.append([line[idx] for idx in command if idx is not False])
        values = new_values
        print "\t- Header columns: ", header

    # write again
    num_lines = len(values)
    splitted = int(num_lines / MAX_ROW_FOR_FILE) > 0
    if not splitted:
        # case not splitted, re-write file
        print "\t- Re-write file : ", file_path
        with open(file_path, 'wb') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            writer.writerows(values)
        return [file_path]
    else:
        parts = int(num_lines / MAX_ROW_FOR_FILE) + 1
        step = MAX_ROW_FOR_FILE
        write_count = 0
        _, tail = os.path.split(file_path)
        output = []
        for p in range(parts):
            fp = os.path.join(data_path, 'part.%d.%s' % (p, tail))
            print "\t- Create new file : ", fp
            with open(fp, 'wb') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_ALL)
                writer.writerow(header)
                writer.writerows(values[write_count: min(write_count + step, num_lines)])
                write_count += step
            output.append(fp)
        # remove old file
        return output

scenarios = []
count = 0
for fn in list_file:
    print "- Re-format file : ", fn
    result_lst = open_csv_and_reformat_file(fn[1])
    if result_lst:
        for result in result_lst:
            count += 1
            dat = [count, fn[0], result]
            scenarios.append(dat)

if scenarios:
    # login via xmlrpc
    host = odoo_configuration_user['url']
    db = odoo_configuration_user['database']
    user = odoo_configuration_user['login']
    pwd = odoo_configuration_user['password']
    # login
    reqs = authenticate_xmlrpc(host, db, user, pwd)
    print reqs.text
    result = simplejson.loads(reqs.text)["result"]
    session_id = result["session_id"]
    partner_id = result["partner_id"]
    # import scenarios
    for item in scenarios:
        print "-- Start importing file : ", item[2]
        # for native import from Odoo
        _, tail = os.path.split(item[2])
        print tail
        if tail in DEDICATED_LST:
            print "SKIP FILE : ", tail
            continue
        request_import_via_csv(host,
                               reqs,
                               db, item[1], item[2])
