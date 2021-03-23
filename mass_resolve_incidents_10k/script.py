#!/usr/bin/env python3
# mass resolve incidents on a PagerDuty account, even if they are more than 10k
# requires a global API KEY with read & write permissions on the account

import requests
import argparse

def get_incidents_list():
    return [200,300]

def resolve_incident(incident_id):
    if args.debug:
        print(f"DEBUG: resolve_incident: working on incident id: {incident_id}")

if __name__ == '__main__':

    # get the api key
    parser = argparse.ArgumentParser(description='Mass resolve incidents on PagerDuty account')
    parser.add_argument('-a', '--api-key', required=True, help='global api key from your PagerDuty account')

    # get the optional filters - service_id, team_id, status, urgencies
    parser.add_argument('-st', '--status-triggered', action='store_const', const='triggered', help='get incidents which have been triggered in your PagerDuty account.')
    parser.add_argument('-sa', '--status-acknowledged', action='store_const', const='acknowledged', help='get incidents which have been acknowledged in your PagerDuty account.')
    parser.add_argument('-sid', '--service-id', action='append', help='get incidents from a given service id from your PagerDuty account. multiple service id\'s can be given seperated by a comma(,)')
    parser.add_argument('-tid', '--team-id', action='append', help='get incidents from a team from your PagerDuty account. multiple team id\'s can be given seperated by a comma(,)')

    parser.add_argument('-d', '--debug', action='store_true',help='show detailed messages on stdout')
    args = parser.parse_args()

    if args.debug:
        print(f"DEBUG: main: command line arguments passed: {args}")

    # establish a requests session
    pd_session = requests.Session()
    pd_session.headers.update({
        'accept': "application/vnd.pagerduty+json;version=2",
        'content-type': "application/json",
        'authorization':f'Token token={args.api_key}'
        }
    )
    
    if args.debug:
        print(f"DEBUG: main: pd_session object: {pd_session.headers}")

    incidents_list = get_incidents_list()
    incidents_count = len(incidents_list)

    if args.debug:
        print(f"DEBUG: main: total incidents found: {incidents_count}")

    # resolve the incidents
    if incidents_count > 0:
        for incident_id in incidents_list:
            
            if args.debug:
                print(f"DEBUG: main: trying to resolve incident: {incident_id}")

            resolve_incident(incident_id)

    else:
        print("no incidents resolved. quitting now.")
