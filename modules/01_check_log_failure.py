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
THRESHOLD = 300
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
    estack.basicQuery(period=PERIOD)

    # required a api call modification based on the query
    result = estack.es.count(index=index, body=estack.query)
    debugging(args, query=estack.query, result=result)

    # logic to trigger the emails. set subject and body to send the emails to the listed recepients
    if result['count'] < THRESHOLD:
        org = "[ " + config.get('GENERAL', 'ORG') + " ] "
        mailbody = "Log count during last 5 minutes reached to {count}".format(count=result['count'])
        em = EmailReport(subject=org + "Alert - Elastic Log Failure Threshold", body=mailbody)
        if args.email:
            em.sendEmail()

if __name__ == '__main__':
    main()

