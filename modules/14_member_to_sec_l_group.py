#! /usr/bin/python3

import os
import sys
import jinja2
import configparser

from datetime import datetime

framework_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
os.chdir(framework_path)
sys.path.append('./classes')

from emailreport import EmailReport
from elasticstack import ElasticStack

## Gloabl variable, if needs to compare against something
THRESHOLD = 0

## MAIN CONFIGURATION FILE PATH
MAIN_CONFIG = "configs/main.cfg"
TEMPLATE_FILE = "table_template.html"
ITEM_PATH_EXCLUSIONS = "exclusions/users/sec_local_group_user.lst"

def main():
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

    ## query needs to overwrite by each script.
    estack.query = query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "winlog.event_id": "4732"
                                }
                            }
                        ],
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "now-5m"
                                    }
                                }
                            }
                        ]
                    }
                }
            }

    # required a api call modification based on the query
    result = estack.es.search(index=index, body=estack.query,  size=1000)

    # logic to trigger tge emails. set subject and body to send the emails to the listed recepients
    count = result['hits']['total']['value']
    if count > THRESHOLD:
        excluded_items = list(map(str.strip, open(ITEM_PATH_EXCLUSIONS, 'r').readlines()))
        hits = result['hits']['hits']

        header = ["Timestamp", "Computer Name", "Executable Path", "Subject User", "Target User", "Target", "Target Server Name"]
        artifacts = [header]
        counter = 0
        for record in hits:
            # from python 3.7 onwards datetime.fromisoformat is available
            source = record['_source']
            event_data = source['winlog']['event_data']
            item = event_data['SubjectUserName']
            _timestamp = datetime.strptime(source['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S")

            if item not in excluded_items:
                artifacts.append([_timestamp, source['winlog']['computer_name'], event_data['SubjectUserName'], event_data['TargetUserName'], event_data['SubjectUserSid'], event_data['PrivilegeList'], event_data['MemberName']])
                counter+=1

        if counter :
            table = template.render(artifacts=artifacts)
            
            org = "[ " + config.get('GENERAL', 'ORG') + " ] "
            mailbody = "{counter}/{count} Adding a member to security-enabled local group events were detected during last 5 minutes\n\n".format(counter=counter, count=count)
            em = EmailReport(subject=org + "Alert - A member added to security-enabled local group [Excluding the defined exclusions]", body=mailbody, table=table)
            em.sendEmail()

if __name__ == '__main__':
    main()

