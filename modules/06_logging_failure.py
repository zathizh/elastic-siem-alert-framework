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
THRESHOLD = 4
PERIOD = '5m'
EVENTID = 4625

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
    estack.setRangeQuery(event_id=EVENTID, period=PERIOD)

    # required a api call modification based on the query
    result = estack.es.search(index=index, body=estack.query, size=1000)
    debugging(args, query=estack.query, result=result)

    # logic to trigger the emails. set subject and body to send the emails to the listed recepients
    count = result['hits']['total']['value']
    if count > THRESHOLD:
        hits = result['hits']['hits']

        protocol= config.get('GENERAL', 'SCHEME')
        baseurl= config.get('GENERAL', 'FQDN')
        port= config.get('GENERAL', 'PORT')

        header =  ["Timestamp", "User Name", "Computer Name", "URL"]
        artifacts = [header]

        for record in hits:
            if args.debug:
                print(record['_source'])
            # from python 3.7 onwards datetime.fromisoformat is available
            _index = record['_index']
            _id = record['_id']
            _timestamp = datetime.strptime(record['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S")
            if 'user' in record['_source']:
                _username = record['_source']['user']['name']
            else:
                _username = ""

            _computername = record['_source']['winlog']['computer_name']

            _url = "{protocol}://{baseurl}:{port}/{_index}/_doc/{_id}".format(protocol=protocol, baseurl=baseurl, port=port, _index=_index, _id=_id)
            artifacts.append([_timestamp, _username, _computername, _url])

        table = template.render(artifacts=artifacts)

        org = "[ " + config.get('GENERAL', 'ORG') + " ] "
        mailbody = "{count} user login failures were detected during last 5 minutes\n\n".format(count=count)
        em = EmailReport(subject=org + "Alert - Login Failure", body=mailbody, table=table)
        if args.email:
            em.sendEmail()

if __name__ == '__main__':
    main()

