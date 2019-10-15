#!/usr/bin/python3

# csv format
# user_name,user_email,user_role
# user_role would be optional. a `user` role would be assumed by the script if not specified explicitly
# this can be changed in the default_role variable definition below
# role can be admin, limited_user, observer, owner, read_only_user, restricted_access, read_only_limited_user or user
# account must have the `read_only_users` ability to set a user as a `read_only_user` or a `read_only_limited_user`, 
# and must have advanced permissions abilities to set a user as `observer` or `restricted_access`.

import requests
import csv

api_token = 'sdXDztGLsq_f7za-teR_'
from_email = 'shivinder@gmail.com'
default_role = 'user'

# maintain a count
total_users = 0

# parse the csv file and display the count and data on screen to get a confirmation from the user
with open('input.csv','r') as input_file:
    csv_file = csv.reader(input_file)

    # the PagerDuty API documentation schema states the following compulsory fields
    # user_name, user_email
    # unless a user_type column is specified in the csv file, we will assume a user role as default

    for row in csv_file:
        user_name = row[0]
        user_email = row[1]
        
        try:
            user_role = row[2]
        except:
            user_role = default_role
        finally:
            if user_role == '':
                user_role = default_role
        
        print('Will create a new user - {} - having an email - {} - with the {} permissions on the account.'.format(user_name,user_email,user_role))

        total_users+=1

user_approval = input('Proceed with creating {} users on the account (y/n)? '.format(total_users))
if user_approval == 'y':
    # define headers for the api call
    url = 'https://api.pagerduty.com/users'
    header =    {
                    'Accept': 'application/vnd.pagerduty+json;version=2',
                    'Content-Type': 'application/json',
                    'From': from_email,
                    'Authorization': 'Token token=' + api_token 
                }

    with open('input.csv','r') as input_file:
        csv_file = csv.reader(input_file)

        # the PagerDuty API documentation schema states the following compulsory fields
        # user_name, user_email and user_type
        # unless a user_type column is specified in the csv file, we will assume a user role as default

        payload = {}
        for row in csv_file:
            user_name = row[0]
            user_email = row[1]
            try:
                user_role = row[2]
            except:
                user_role = default_role
            finally:
                if user_role == '':
                    user_role = default_role

            print('user_name: {}, user_email: {}, user_role: {}'.format(user_name,user_email,user_role))
            # create a payload for the new user
            payload = {
                    'user': {
                        'type': 'user',
                        'name': user_name,
                        'email': user_email,
                        'role': user_role
                    }
                }
            
            response = requests.post(url,headers=header,json=payload)

            if response.ok: 
                print('User - {} - with email - {} - created successfully in the account.'.format(user_name,user_email))
            else:
                print('Received a response code {} for the request. Details - {}'.format(response.status_code,response.text))

else:
    print('Quitting script.')