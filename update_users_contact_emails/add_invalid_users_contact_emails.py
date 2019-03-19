#!/usr/bin/env python3
# REST API Guide: https://api-reference.pagerduty.com
# Just needs the API Token from the Account Owner to run
# TODO: exception handling when no/invalid api_token is passed
#       minor tweaks :)

import requests
import json

# account definitions
api_token = 'xxx'
url = 'https://api.pagerduty.com/users'
header =    {
                'Accept':'application/vnd.pagerduty+json;version=2',
                'Content-Type': 'application/json', 
                'Authorization':'Token token=' + api_token 
            }

## added pagination support
# switch to max result limit (as specified on PD documentation website)
limit = 100
offset = 0

# maintain a count
total_scanned,total_updates = 0, 0

while True:
    params = {'include[]': 'contact_methods', 'limit': limit, 'offset': offset}

    # Get the list of users from PD with their contact emails and convert it to JSON
    users_list = json.loads(requests.get(url, params=params, headers=header).text)

    for user in users_list['users']:
        # working example: print(users_list['users'][0]['contact_methods'][0]['address'])
        uid = user['id']
        
        # this loop handles multiple contact emails, if any, for one user
        for contact_method in user['contact_methods']:
            if contact_method['type'] == 'email_contact_method':
                # update the total count
                total_scanned+=1

                # fetch the required values
                current_contact_method_id = contact_method['id']
                current_contact_method_label = contact_method['label']
                current_contact_method_email = contact_method['address']
                print("[" + uid + "] [" + str(current_contact_method_id) + "] " + str(current_contact_method_email))

                # condition to check if .invalid is already there in the email
                if current_contact_method_email[-8:] == '.invalid':
                    print('SKIPPED - ' + current_contact_method_email + '\n')
                    continue
                
                # update count
                total_updates+=1

                # form the new payload for the api request to change the current contact email to the new one
                payload = {
                    'contact_method': {
                        'type': 'email_contact_method',
                        'label': current_contact_method_label,
                        'address': current_contact_method_email + '.invalid'
                    }
                }

                # form the new url for the api request
                update_url = url + '/{}/contact_methods/{}'.format(uid,current_contact_method_id)

                # fire the request. for some reason had to convert payload to str
                response = requests.put(update_url, headers=header, data=str(payload))

                if response.status_code == 200:
                    print('SUCCESS - ' + current_contact_method_email + '.invalid')
                else:   
                    print('FAILED - ' + current_contact_method_email + ' - ' + response.text)
                print('\n')
    
    # condition to break out of infinite while loop
    if users_list['more'] == True:
        offset+=limit
    else:
        break

# print stats on cli
print('Total contact methods scanned: {}\nTotal contact methods changed: {}\nTotal pages fetched: {}'.format(str(total_scanned),str(total_updates),str((offset//limit)+1)))