#!/usr/bin/python3
# Script to fetch the first_trigger_log_entry values for all incidents in a service within a given time frame
# works on one service only

import argparse

# define command line arguments - api-key and service
parser = argparse.ArgumentParser(description='Get a list of all incidents on a service.')
parser.add_argument('--api-key', required=True, type=str, help='REST API key from the account owner. Can be a read-only key.')
parser.add_argument('--service', required=True, type=str, help='Service ID from the account.')
parser.add_argument('--since', required=True, type=str, help='Begin date to fetch the incidents.')
parser.add_argument('--until', required=True, type=str, help='End date to fetch the incidents.')

args = parser.parse_args()

url = 'https://api.pagerduty.com/incidents'
header =    {
                'Accept':'application/vnd.pagerduty+json;version=2',
                'Authorization':'Token token=' + args.api_key
}

# pagination support - switch to max result limit (as specified on PD documentation website)
limit = 100
offset = 0

# maintain a count of the incidents
total_incidents = 0

# get the lib's for the task
import requests
import csv
import json

file_name = 'incidents_list_from_{}_to_{}.csv'.format(args.since,args.until)

with open(file_name,'w') as output_file:
    csv_file = csv.writer(output_file)

    # Start looping through the incidents
    while True:
        params = {
            'include[]': 'first_trigger_log_entries',
            'service_ids[]': args.service, 
            'since': args.since,
            'until': args.until,
            'limit': limit,
            'offset': offset
        }

        # make the request
        incidents_list = requests.get(url, params=params, headers=header).json()

        # print(incidents_list)

        for incident in incidents_list['incidents']:

            # update the count
            total_incidents += 1

            # fetch the field values
            incident_number = incident['incident_number']
            incident_id = incident['id']
            incident_title = incident['title']
            incident_created_at = incident['created_at']
            incident_first_trigger_log_entry = json.dumps( incident['first_trigger_log_entry'] )

            # write the data to the csv file
            csv_file.writerow([incident_number,incident_id,incident_title,incident_created_at,incident_first_trigger_log_entry])

        # condition to break out of infinite while loop
        if incidents_list['more'] == True:
            offset+=limit
        else:
            break

# print some stats on the screen
print('total incidents fetched: {}\nResults saved in file - {}'.format(total_incidents, file_name))