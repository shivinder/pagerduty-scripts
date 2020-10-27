#!/usr/bin/python3
# Modify user object attributes
# Possible user object attributes which can be modified are: name, email, time_zone, role, description, job_title
#
# the script searches the object with the user email address and proceeds to modify the attributes specified in the next column
# the columns should have the headers to identify the column values

import pandas as pd
import sys
import json
import requests
import argparse

def fetch_all_users():
    users_list = list()

    # pagination support - stll using the classic pagination
    limit = 100 # max value mentioned in the PD documentation
    offset = 0

    # fetch all the users from account
    more = True
    while more:
        querystring = {
            'limit': limit,
            'offset': offset,
            'total': "false"
        }

        # fetch the initial batch of users
        response = json.loads(requests.get('https://api.pagerduty.com/users', headers=header, params=querystring).text)
        more = response['more']
        offset += limit

        users_list.extend(response['users'])
    
    return users_list

def update_user_attribute(user_id, user_type, user_name, user_email, user_attribute_type, user_attribute_value):
    # check for job_title. value should be between 1..100
    if user_attribute_type == 'job_title' and user_attribute_value == '':
        user_attribute_value = ' '

    # required parameters are: type, name, email
    payload = {
        'user': {
            'type': user_type,
            'name': user_name,
            'email': user_email,
            f'{user_attribute_type}': user_attribute_value
        }
    }

    print(f"Updating {user_attribute_type} for {user_name} with the new value of {user_attribute_value}")
    
    requests.put("https://api.pagerduty.com/users/" + user_id, headers=header, json=payload)

def run_custom_dataframe_checks(df):
    # basic checks based on the number of columns in the csv file
    if len(df.columns) > 1:
        if not df.columns[0] == 'email':
            print(f"The first header in the csv file must be email. Exiting now.")
            sys.exit()
        else:
            # list of editable user object attributes
            user_object_attributes = {'name', 'email', 'time_zone', 'role', 'description', 'job_title'}
            for df_cols in df.columns:
                if df_cols not in user_object_attributes:
                    print(f"Column header \"{df_cols}\" not found in valid user object attributes. Column headers should be one of these - {user_object_attributes}")
                    sys.exit()
    else:
        print(f"Number of columns is too less to run the script. Exiting now.")
        sys.exit()

    return df

def main():
    df = run_custom_dataframe_checks(pd.read_csv(args.file_name))

    # fetch a list of all users in the account 
    users_list = fetch_all_users()

    for df_row in df.itertuples():
        user_found = False
        for user in users_list:
            # we have a match
            if df_row.email == user['email']:
                user_found = True
                for df_col_title in df.columns:
                    update_user_attribute(user['id'], user['type'], user['name'], user['email'], df_col_title, getattr(df_row, df_col_title) )

        if not user_found:
            print(f"Skipping user with email address \"{df_row.email}\" not found in the account")

if __name__ == "__main__":
    # parse the command line arguments
    parser = argparse.ArgumentParser(description='Modify user object attributes based on the column headers supplied in the csv file. \
        The script supports changing the name, email, time_zone, role, description, job_title.')
    parser.add_argument('-a', '--api-key', required=True, help='global api key from the account')
    parser.add_argument('-f', '--file-name', required=True, help='path of the csv file to be parsed')
    args = parser.parse_args()

    # define the generic header to be used in all api requests
    header = {
            'accept': "application/vnd.pagerduty+json;version=2",
            'content-type': "application/json",
            'authorization': "Token token=" + args.api_key
    }

    main()