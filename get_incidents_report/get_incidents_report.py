#!/usr/bin/env python3
# we would be using the List Incidents api endpoint to fetch a list of all the incidents on one service in a PagerDuty account
# official api documentation for List Incidents - https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1incidents/get

import argparse
import requests
import json
import csv

def get_incidents(session, service_ids=False):
    # handle pagination - incidents endpoint does not support cursor based pagination. using classic pagination
    # more details about pagination here - https://developer.pagerduty.com/docs/rest-api-v2/pagination
    limit, offset, more, total = 100, 0, True, False

    if service_ids:
        service_ids = service_ids.split(",")

    # define the parameters for the requests get call
    querystring = {"service_ids[]": service_ids, "total": total, "limit": limit, "offset": offset, "time_zone": "UTC"}

    incidents_list = []
    try:
        while more:
            incidents_list_batch = json.loads(session.get('https://api.pagerduty.com/incidents', params=querystring).text)
            incidents_list.extend(incidents_list_batch['incidents'])
            offset += limit
            more = incidents_list_batch['more']

        return incidents_list

    except Exception as ex:
        print(f'An exception occured while connecting to the PagerDuty account. Exception details - {str(ex)}')
        return False

def generate_csv_report(incidents_list):
    # incidents reponse fields can be seen from the official documentation here - https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1incidents/get
    # displaying -> number, id, status, title, service link, ep link, created_at, last_status_change_by, 

    incidents_data = []
    # fetch the data from the json and nicely place them in vars for readibility
    for incident in incidents_list:
        incident_number = incident['incident_number']
        incident_id = incident['id']
        incident_status = incident['status']
        incident_title = incident['title']
        service_link = incident['service']['html_url']
        ep_link = incident['escalation_policy']['html_url']
        incident_created_at = incident['created_at']
        incident_last_status_change_by = incident['last_status_change_by']['html_url']
        incident_last_status_change_at = incident['last_status_change_at']
        # keep appending the data to the list which will be written to the csv file in the next step
        incidents_data.append([incident_number, incident_id, incident_status, incident_title, service_link, ep_link, incident_created_at, incident_last_status_change_by, incident_last_status_change_at])

    # write to csv file
    with open('incidents_report.csv','w') as csv_fh:
        csv_file = csv.writer(csv_fh)
        # write the headers
        csv_file.writerow(['incident number', 'incident id', 'incident status', 'incident title', 'service', 'escalation policy', 'created at', 'last status change by', 'last status change at'])
        csv_file.writerows(incidents_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate the incidents report.', epilog='Find more details in the accompanying README.md')
    parser.add_argument('--api-key', '-k', type=str, required=True, help='Global API key of your PagerDuty account')
    parser.add_argument('--service-ids', '-s', type=str, required=False, help='Optionally you may supply a Service ID to generate a report for the supplied Service ID. You may supply more than one Service ID associated with your account seperated by commas, example PXXXXX1,PXXXXX2')
    args = parser.parse_args()

    with requests.Session() as session:
        session.headers.update({"Accept": "application/vnd.pagerduty+json;version=2", "Content-Type": "application/json", "Authorization": "Token token={}".format(args.api_key)})
        incidents_list = get_incidents(session, args.service_ids)

    if incidents_list:
        generate_csv_report(incidents_list)
    else:
        print('\nIncidents report could not be generated.')