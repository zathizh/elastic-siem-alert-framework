import argparse

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False, help='debug on/off')
    parser.add_argument('-e', '--email', action='store_true', required=False, help='enable email notifications')
    parser.add_argument('-q', '--query', action='store_true', required=False, help='display query')
    parser.add_argument('-o', '--object', action='store_true', required=False, help='display json object')
    parser.add_argument('-r', '--range', required=False, help='time Period')
    args = parser.parse_args()
    return args
