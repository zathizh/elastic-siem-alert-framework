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
PERIOD = '5m'

## MAIN CONFIGURATION FILE PATH
MAIN_CONFIG = "configs/main.cfg"
TEMPLATE_FILE = "table_template.html"
ITEM_IMAGE_PATH_EXCLUSIONS = "exclusions/services/image_paths.lst" 

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
    estack.setRangeQuery(event_id=7045, period=PERIOD)

    # required a api call modification based on the query
    result = estack.es.search(index=index, body=estack.query, size=1000)
    debugging(args, query=estack.query, result=result)

    # logic to trigger tge emails. set subject and body to send the emails to the listed recepients
    count = result['hits']['total']['value']
    if count > THRESHOLD:
        excluded_items = list(map(str.strip, open(ITEM_IMAGE_PATH_EXCLUSIONS, 'r').readlines()))
        hits = result['hits']['hits']

        header = ["Timestamp", "Computer Name", "Provider Name", "Image Path", "Service Name", "Service Type"]
        artifacts = [header]
        counter = 0
        for record in hits:
            # from python 3.7 onwards datetime.fromisoformat is available
            source = record['_source']['winlog']
            event_data = source['event_data']
            item = source['event_data']['ImagePath']
            _timestamp = datetime.strptime(record['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S")

            if item not in excluded_items:
                if args.debug:
                    item
                artifacts.append([_timestamp, source['computer_name'], source['provider_name'], event_data['ImagePath'], event_data['ServiceName'], event_data['ServiceType']])
                counter+=1

        if counter :
            table = template.render(artifacts=artifacts)
            
            org = "[ " + config.get('GENERAL', 'ORG') + " ] "
            mailbody = "{counter}/{count} New Service installations were detected during last 5 minutes\n\n".format(counter=counter, count=count)
            em = EmailReport(subject=org + "Alert - Service Installed [Excluding the defined exclusions]", body=mailbody, table=table)
            em.sendEmail()

if __name__ == '__main__':
    main()

