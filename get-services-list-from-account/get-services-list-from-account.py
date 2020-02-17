#!/usr/bin/python3
# fetch a list of all users on the account and save it to a csv file

import requests
import argparse
import csv

parser = argparse.ArgumentParser(description='Get a list of all services and their integrations on a PagerDuty account.')
parser.add_argument('-k', '--api-key', required=True, type=str, help='REST API key from the account owner.')

args = parser.parse_args()

url = 'https://api.pagerduty.com/services'
header =    {
                'Accept':'application/vnd.pagerduty+json;version=2',
                'Content-Type': 'application/json', 
                'Authorization':'Token token=' + args.api_key
            }

## added pagination support
# switch to max result limit (as specified on PD documentation website)
limit = 100
offset = 0

# open the csv file
with open('services_and_integratons_list.csv','w') as output_file:
    csv_file = csv.writer(output_file)

    while True:
        params = {'include[]': 'integrations', 'limit': limit, 'offset': offset}

        # Get the list of users from PD with their contact emails in JSON
        services_list = requests.get(url, params=params, headers=header).json()

        for service in services_list['services']:
            service_id = service['id']
            service_name = service['name']

            for integration in service['integrations']:
                integration_id = integration['id']
                integration_type = integration['type']
                integration_summary = integration['summary']

                # write data to the output csv file - more verbose
                #csv_file.writerow([service_id,service_name,integration_id,integration_type,integration_summary])
                # write data to the output csv file - to match existing sql query format
                csv_file.writerow([service_name,integration_summary,integration_type])

        # condition to break out of infinite while loop
        if services_list['more'] == True:
            offset += limit
        else:
            break