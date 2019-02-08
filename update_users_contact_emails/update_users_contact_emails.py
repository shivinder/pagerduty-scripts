# Just need the API Token from the Account Owner to run

import requests
import json

# Definitions
api_token = 'xxx'
header = {'Accept':'application/vnd.pagerduty+json;version=2', 'Content-Type': 'application/json', 'Authorization':'Token token=' + api_token}
url = 'https://api.pagerduty.com/users'

# Get the list of users from PD with their contact emails
response = requests.get(url, params='include[]=contact_methods', headers=header)

# Convert the result to JSON
users_list = json.loads(response.text)

# maintain a count
total_updates = 0

for user in users_list['users']:
    # working example: print(users_list['users'][0]['contact_methods'][0]['address'])
    uid = user['id']
    
    # this loop handles multiple contact emails, if any, for one user
    for contact_method in user['contact_methods']:
        if contact_method['type'] == 'email_contact_method':
            # update count
            total_updates+=1
            
            # fetch the required values
            current_contact_method_id = contact_method['id']
            current_contact_method_label = contact_method['label']
            current_contact_method_email = contact_method['address']
            print("[" + uid + "] [" + str(current_contact_method_id) + "] " + str(current_contact_method_email))

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

            # fire the request
            response = requests.put(update_url, headers=header, data=str(payload))

            if response.status_code is 200:
                print('SUCCESS - ' + current_contact_method_email + '.invalid')
            else:   
                print('FAILED - ' + current_contact_method_email + ' - ' + response.text)
            print('\n')

print('Total updates done: ' + str(total_updates))