#!/usr/bin/python3
# Use this script to mass update the incidents behavior in all services in a PagerDuty account
# Two possible options are: Create alerts and incidents, Create incidents

# display the options to the user and get the api key
api_key = input('Please enter the API key for the account: ')
alert_creation = input('The following incident behavior options are available:\n\
1. Create alerts and incidents\n2. Create incidents\n\
Input your option number (1/2): ')

# exit if alert behavior is not 1 or 2
if int(alert_creation) == 1:
    alert_creation = 'create_alerts_and_incidents'
elif int(alert_creation) == 2:
    alert_creation = 'create_incidents'
else:
    exit('Exiting script: Not an expected Service Incident Behavior option selected!')

print('The script will now proceed with changing the services incident behavior to {}'.format(alert_creation))

# import the requests lib, define the variables and request headers
import requests
import json
base_url = 'https://api.pagerduty.com'
header =    {
                'Accept':'application/vnd.pagerduty+json;version=2',
                'Content-Type': 'application/json', 
                'Authorization':'Token token=' + api_key
            }

# get a list of all the services in the account
# update the service with the incident behavior specified
# try:
# PagerDuty Documentation - https://api-reference.pagerduty.com/#!/Services/get_services
services_url = base_url + '/services'
# maintain count variables
total_services = 0
total_services_mofified = 0

# pagination support - switch to max result limit (as specified on PD documentation website)
limit = 100
offset = 0

try:
    # fetch all the services list
    while True:
        params = {'limit': limit, 'offset': offset}

        # Get the list of services from the PagerDuty account
        services_list = json.loads(requests.get(services_url, params=params, headers=header).text)

        for service in services_list['services']:
            total_services += 1
            # skip if service incident behavior is already what the user wants
            if service['alert_creation'] == alert_creation:
                continue

            # update the modified count
            total_services_mofified += 1

            service_id = service['id']
            service_type = service['type']

            update_services_url = services_url + '/' + service_id
            payload = {
                'service': {
                    'type': service_type,
                    'alert_creation': alert_creation
                }
            }

            # update the alert_creation field and fire the service update request
            # https://api-reference.pagerduty.com/#!/Services/put_services_id
            response = requests.put(update_services_url,headers=header,json=payload)
            if response.ok:
                print('Updated service: \"{}\" incident behavior to {}'.format(service['name'],alert_creation))
            else:
                print('ERROR: Service Name: {} received a {} - {}'.format(service['name'],response.status_code,response.text))

        # condition to break out of infinite while loop
        if services_list['more'] == True:
            offset+=limit
        else:
            break

except:
    print('ERROR: Incorrect API Token!')

print('Total services found on account: {}\nServices modified: {}'.format(total_services,total_services_mofified))