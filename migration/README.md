# odoo-script
Extra Script for Migration data

You need to create locally an extra file named cfg_secret_configuration.py with the following code :

```
#! /usr/bin/env python
# -*- encoding: utf-8 -*-

odoo_configuration_user = {
    'url':  'http://my_server.com',
    'database': 'MY_DATABASE',
    'login': 'MY_LOGIN',
    'password': 'MY_PASSWORD',
}

# credentials json path
# how to get credential key : http://gspread.readthedocs.io/en/latest/oauth2.html
credentials_path = 'Credentials JSON file path'
Example : credentials_path = '/opt/openerp/code/project/projects/lalouve_projects/My Project-8844cb4f5e41.json'

# Number of rows for each file csv
#Example : MAX_ROW_FOR_FILE = 500
MAX_ROW_FOR_FILE = xxx

# Link to google sheet data, all links to google-sheets have to be shared with service-account in credentials file
#Example : data_links = "https://docs.google.com/spreadsheets/d/1HC9uF5wi_97MNRhPomYJevkIRG8WytfPeEu8Q9YGjmY/"
data_links = "Single Google Sheets Link"

# A dictionary linked sheets name with Odoo model
# Format for item : {<Name of sheet> : [<output csv file>, <related model in Odoo>]}
data_csv_name = {
    "Users" : ["res.users.csv", 'res.users'],
    "COA": ["account.account.csv", "account.account"],
    "Payment Terms": ["account.payment.csv", "account.payment"],
    "Journals": ["account.journal.csv", "account.journal"],
    "Product Categories": ["product.category.csv", "product.category"],
    "Members": ["members.csv", "res.partner"],
    "Other People": ["other_people.csv", "res.partner"],
    "Pos Product Categories": ["pos.category.csv", "pos.category"],
    "Taxes (generic)": ["account.tax.csv", 'account.tax'],
    "Fiscal Classifications (generic)": ["account.product.fiscal.classification.csv", "account.product.fiscal.classification"],
    "Products": ["product.template.csv", "product.template"],
    "Suppliers": ["suppliers.csv", "res.partner"],
    "Prices": ["product.supplierinfo.csv", "product.supplierinfo"],
    "Shift Templates": ["shift.template.csv", "shift.template"],
    "Scale System Data": ["product.scale.system.csv", "product.scale.system"],
    "Scale System Groups": ["product.scale.group.csv", "product.scale.group"],
    "Scale System Product Lines": ["product.scale.group.product.line.csv", "product.scale.group.product.line"],
    "Scale Group Product Relation": ["product.scale.group.relation.product.csv", "product.template"],
    "Products Coefficients": ["product.coefficient.csv", "product.coefficient"]
}

# A list of file csv which is downloaded but we do not import these data.
DEDICATED_LST = ["members.csv"]

```

1. Running:

Command install:
```
pip install gspread oauth2client
```

Command to run:
```
python connect_and_download_spreadsheet.py <name of sheets>
Example : python connect_and_download_spreadsheet.py COA
Example : python connect_and_download_spreadsheet.py Users COA Journals
```

Note that:
    - For member.csv, we have specific format that it's not fit with native
    import format, so the script will stop at download member.csv
    - For some sheet that it have more lines than MAX_ROW_FOR_FILE, the script
    will split this sheet to many files then import them.
    - When running script, the login account have to be set expected Language.
    - To avoid print all Logs on screen can use `&> log.txt` to print all logs
    into file txt.
        Example : python connect_and_download_spreadsheet.py COA &> log.txt

2. For import product quantity, we should create Inventory Adjustment for each stock location.
Steps :

	- Adjust server information to connect and get data.
	- Download quantity product by stock.
```
python 97_download_stock_quant.py output.csv
Example output : Physical_Locations_WH_Stock_output.csv
```

	- Adjust server information to connect and import data
	- Create Inventory Adjustmennt
```
python import_quantity_on_hand.py Physical_Locations_WH_Stock_output.csv
```

3. To import member
```
python 07_import_member.py imported_member.csv
python 07_import_member.py imported_member.csv --dry-run
```

4. Delete all current member
```
python 07_delete_member.py imported_member.csv
```

3. To download and import member images (adjust server configurations before running command)

	- Download member image
```
python download_import_member_images.py --download <folder_path>
```

	- Upload member image
```
python download_import_member_images.py --upload <folder_path>
```
	- Notes: output image file will be <partner info>.jpeg with <partner info> have to be email or name of partner.
