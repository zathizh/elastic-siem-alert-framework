#! /usr/bin/python3

import os
import sys
import configparser

from datetime import datetime
from elasticsearch import Elasticsearch
from ssl import create_default_context

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

    def basicQuery(self, period):
        self.query = {
                "query":{
                    "range": {
                        "@timestamp": {
                            "gte": "now-" + period
                            }
                        }
                    }
                }

    def setRangeQuery(self, event_id, period):
        self.query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "winlog.event_id": event_id
                                    }
                                }
                            ],
                        "filter": [
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": "now-" + period
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }

    def setElementQuery(self, event_id, period):
        self.query = {
                "size": 0,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "winlog.event_id": event_id
                                    }
                                }
                            ],
                        "filter": [
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": "now-" + period
                                        }
                                    }
                                }
                            ]
                        }
                    },
                "aggs": {
                    "element": {
                        "terms": {
                            "field": "user.name",
                            "size": 100000
                            }
                        }
                    }
                }


