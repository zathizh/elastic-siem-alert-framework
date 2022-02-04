#! /usr/bin/python3

import os
import sys
import configparser

framework_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
os.chdir(framework_path)
sys.path.append('./classes')

from emailreport import EmailReport
from elasticstack import ElasticStack

## Gloabl variable, if needs to compare against something
THRESHOLD = 300

## MAIN CONFIGURATION FILE PATH
MAIN_CONFIG = "configs/main.cfg"

def main():
    # create elastic stack object
    estack = ElasticStack()

    # handle log index
    config = configparser.ConfigParser(delimiters=('='))
    config.read(MAIN_CONFIG)

    index = config.get('CONFIGURATIONS', 'INDEX')

    ## query needs to overwrite by each script.
    estack.query = query = {
            "query":{
                "range": {
                    "@timestamp": {
                        "gte": "now-5m"
                        }
                    }
                }
            }


    # required a api call modification based on the query
    result = estack.es.count(index=index, body=estack.query)

    # logic to trigger the emails. set subject and body to send the emails to the listed recepients
    if result['count'] < THRESHOLD:
        mailbody = "Log count during last 5 minutes reached to {count}".format(count=result['count'])
        em = EmailReport(subject="Alert - Elastic Log Failure Threshold", body=mailbody)
        em.sendEmail()

if __name__ == '__main__':
    main()

