#! /usr/bin/python3

import os
import sys
import jinja2
import configparser

from datetime import datetime

framework_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
os.chdir(framework_path)
sys.path.append('./classes')

from handler import *
from argumentparser import *
from emailreport import EmailReport
from elasticstack import ElasticStack

## Gloabl variable, if needs to compare against something
THRESHOLD = 0
PERIOD = '1h'

## MAIN CONFIGURATION FILE PATH
MAIN_CONFIG = "configs/main.cfg"
TEMPLATE_FILE = "table_template.html"

def main():
    # handling debug arguments
    args = getArgs()
    global PERIOD
    PERIOD = args.range or PERIOD

    # create elastic stack object
    estack = ElasticStack()

    # handle log index
    config = configparser.ConfigParser(delimiters=('='))
    config.read(MAIN_CONFIG)

    # handle jinja2 templates
    templateLoader = jinja2.FileSystemLoader(searchpath="templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(TEMPLATE_FILE)

    index = config.get('CONFIGURATIONS', 'INDEX')

    ## query id needs to change for each script
    estack.setUserQuery(event_id=4634, period=PERIOD)

    # required a api call modification based on the query
    result = estack.es.search(index=index, body=estack.query, size=1000)
    debugging(args, query=estack.query, result=result)

    # logic to trigger the emails. set subject and body to send the emails to the listed recepients
    count = result['hits']['total']['value']
    if count > THRESHOLD:
        hits = result['aggregations']['username']['buckets']

        header = ["User Name", "Count"]
        artifacts = [header]
        for record in hits:
            # from python 3.7 onwards datetime.fromisoformat is available
            artifacts.append([record['key'],record['doc_count']])

        table = template.render(artifacts=artifacts)

        org = "[ " + config.get('GENERAL', 'ORG') + " ] "
        mailbody = "{count} user logoffs were detected during last 1 hour\n\n".format(count=count)
        em = EmailReport(subject=org + "Alert - Unusual Logoff", body=mailbody, table=table)
        if args.email:
            em.sendEmail()

if __name__ == '__main__':
    main()

