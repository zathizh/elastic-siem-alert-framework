#! /usr/bin/python3

import os
import sys
import configparser

from datetime import datetime
from elasticsearch import Elasticsearch
from ssl import create_default_context

#os.chdir('/home/linuxadmin/scripts')
#sys.path.append('./classes')
from emailreport import EmailReport

## MAIN CONFIGURATION FILE PATH
MAIN_CONFIG = "configs/main.cfg"

class ElasticStack:
    def __init__(self, query=None):
        config = configparser.ConfigParser(delimiters=('='))
        config.read(MAIN_CONFIG)

        fqdn = config.get('GENERAL', 'FQDN')
        scheme = config.get('GENERAL', 'SCHEME')
        port = config.get('GENERAL', 'PORT')
        cafile = config.get('GENERAL', 'CA_FILE_PATH')
        use_ssl = config.get('GENERAL', 'SSL')

        http_auth_username = config.get('CREDENTIALS', 'USERNAME')
        http_auth_password = config.get('CREDENTIALS', 'PASSWORD')

        context = create_default_context(cafile=cafile)
        self.es = Elasticsearch(
                [fqdn],
                http_auth=(http_auth_username, http_auth_password),
                scheme=scheme,
                port=port,
                use_ssl=use_ssl,
                ssl_context=context,
                )
        self.query = ""

