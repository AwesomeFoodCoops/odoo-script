# odoo-script
Extra Script for Louve Project

you need to create locally an extra file named cfg_secret_configuration.py with the following code :

```
#! /usr/bin/env python
# -*- encoding: utf-8 -*-

odoo_configuration_user = {
    'url':  'http://my_server.com',
    'database': 'MY_DATABASE',
    'login': 'MY_LOGIN',
    'password': 'MY_PASSWORD',
}
```
