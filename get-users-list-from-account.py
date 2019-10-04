#!/usr/bin/python3
# fetch a list of all users on the account and save it to a csv file

import requests
import csv

api_token = 'XXX'
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
total_users = 0

# open the csv file
with open('user_list.csv','w') as output_file:
    csv_file = csv.writer(output_file)

    while True:
        params = {'include[]': 'contact_methods', 'limit': limit, 'offset': offset}

        # Get the list of users from PD with their contact emails in JSON
        users_list = requests.get(url, params=params, headers=header).json()

        for user in users_list['users']:
            total_users += 1
            user_id = user['id']
            user_name = user['name']
            user_email = user['email']

            # write data to the output csv file
            csv_file.writerow([user_id,user_name,user_email])

        # condition to break out of infinite while loop
        if users_list['more'] == True:
            offset+=limit
        else:
            break

print('total users in the account: {}'.format(total_users))