#!/usr/bin/python3

# csv format - user_role & job_title are optional
# user_name,user_email,user_role,job_title

# user_role would be optional. a `user` role would be assumed by the script if not specified explicitly
# this can be changed in the default_role variable definition below
# role can be admin, limited_user, observer, owner, read_only_user, restricted_access, read_only_limited_user or user
# account must have the `read_only_users` ability to set a user as a `read_only_user` or a `read_only_limited_user`, 
# and must have advanced permissions abilities to set a user as `observer` or `restricted_access`.

api_token = input('Please enter the API token for the account: ')
if api_token == '':
    exit('An API token is required to run the script!')

from_email = input('Please enter the "From Email" address. This would be used to send out the invitation emails: ')
if from_email == '':
    exit('A "From Email" address is required to send out the email invites.')

import requests
import csv

# ToDo: define various different roles here?
default_role = 'user'
default_title = ''

# maintain a count
total_users = 0

input('Please ensure that the CSV file name is "input.csv" and it is in the same directory as this script.\nPress any key to begin the import process...\n')

# parse the csv file and display the count and data on screen to get a confirmation from the user
with open('input.csv','r') as input_file:
    csv_file = csv.reader(input_file)

    # the PagerDuty API documentation schema states the following compulsory fields
    # user_name, user_email
    # unless a user_type column is specified in the csv file, we will assume a user role as default

    for row in csv_file:
        user_name = row[0]
        user_email = row[1]
        
        # define user_role from CSV else use default values
        try:
            user_role = row[2]
        except:
            user_role = default_role
        finally:
            if user_role == '':
                user_role = default_role
        
        # define job_title from CSV else use default values
        try:
            job_title = row[3]
        finally:
            job_title = default_title

        print('Will create a new user "{}" with a job title of "{}" having an email "{}" with "{}" permissions.'.format(user_name,job_title,user_email,user_role))

        total_users+=1

# maintain a count of users added successfully
total_added = 0

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

            # create a payload for the new user
            payload = {
                    'user': {
                        'type': 'user',
                        'name': user_name,
                        'email': user_email,
                        'role': user_role,
                        'job_title': job_title
                    }
                }
            
            response = requests.post(url,headers=header,json=payload)

            if response.ok: 
                print('User - {} - with email - {} - created successfully in the account with the {} role.'.format(user_name,user_email,user_role))
                total_added+=1
            else:
                print('Received a response code {} for the request. Details - {}'.format(response.status_code,response.text))

else:
    print('You selected not to proceed. Quitting script now. No changes to the account have been made.')

print('\n\nTotal users supplied - {}\nTotal users added by script - {}\nTotal users skipped - {}\n'.format(total_users,total_added,total_users-total_added))