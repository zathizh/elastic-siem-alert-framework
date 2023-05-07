#! /usr/bin/python3

import os
import sys
import configparser

framework_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
os.chdir(framework_path)
sys.path.append('./classes')

from handler import *
from argumentparser import *
from emailreport import EmailReport
from elasticstack import ElasticStack

## Gloabl variable, if needs to compare against something
THRESHOLD = 0
PERIOD = '5m'

## MAIN CONFIGURATION FILE PATH
MAIN_CONFIG = "configs/main.cfg"

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

    index = config.get('CONFIGURATIONS', 'INDEX')

    ## query id needs to change for each script
    estack.setRangeQuery(event_id=4104, period=PERIOD)

    # required a api call modification based on the query
    result = estack.es.search(index=index, body=estack.query, size=1000)
    debugging(args, query=estack.query, result=result)

    # logic to trigger tge emails. set subject and body to send the emails to the listed recepients
    if result['count'] > THRESHOLD:
        org = "[ " + config.get('GENERAL', 'ORG') + " ] "
        mailbody = "{count} PowerShell scriptblock loggings were detected during last 5 minutes".format(count=result['count'])
        em = EmailReport(subject=org + "Alert - PowerShell scriptblock logging", body=mailbody)
        em.sendEmail()

if __name__ == '__main__':
    main()

