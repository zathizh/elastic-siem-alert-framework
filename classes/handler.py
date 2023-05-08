from datetime import datetime

def debugging(args, query, result):
    if args.object:
        print(result)
    if args.query:
        print(query)

def controller_exc(excludedItems, hits, header, itemName, fieldList, debug):
    artifacts = [header]
    counter = 0
    
    for record in hits:
        source = record['_source']
        event_data = source['winlog']['event_data']
        comp_name = source['winlog']['computer_name']
        item = event_data[itemName]

        # from python 3.7 onwards datetime.fromisoformat is available
        _timestamp = datetime.strptime(source['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S")
        
        if item not in excludedItems:
            if debug:
                print(item)
            artifacts.append([_timestamp, comp_name] + list(map(event_data.get, fieldList)))
            counter+=1

    return counter, artifacts


def controller(hits, header, evt, fieldList, debug, src=None):
    artifacts = [header]

    for record in hits:
        source = record['_source']

        if src and evt is None:
            event_data = source[src]
        else : 
            event_data = source["winlog"][evt]

        comp_name = source['winlog']['computer_name']

        # from python 3.7 onwards datetime.fromisoformat is available
        _timestamp = datetime.strptime(source['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S")

        if debug:
            print(event_data)
        artifacts.append([_timestamp, comp_name] + list(map(event_data.get, fieldList)))

    return artifacts


def controller_agg(hits, header):
    artifacts = [header]
    for record in hits:
        # from python 3.7 onwards datetime.fromisoformat is available
        artifacts.append([record['key'],record['doc_count']])

    return artifacts
