#!/usr/bin/python3
# Modify user object attributes
# Possible user object attributes which can be modified are: name, email, time_zone, role, description, job_title
#
# the script searches the object with the user email address and proceeds to modify the attributes specified in the next column
# the columns should have the headers to identify the column values

import pandas as pd # required to work on the csv files
import numpy as np  # imported just to do the np.nan comparisions
import sys
import json
import requests
import argparse

def fetch_all_users(api_key):
    users_list = []

    header = {
        'accept': "application/vnd.pagerduty+json;version=2",
        'content-type': "application/json",
        'authorization': "Token token=" + api_key
    }

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

def update_user_attribute(api_key, user_id, user_type, user_name, user_email, user_attribute_type, user_attribute_value):
    header = {
            'accept': "application/vnd.pagerduty+json;version=2",
            'content-type': "application/json",
            'authorization': "Token token=" + api_key
    }

    # check for job_title. value should be between 1..100
    job_title_empty = False
    if user_attribute_type == 'job_title' and user_attribute_value.strip() == '':
        job_title_empty = True
        user_attribute_value = ' '

    # required parameters are: type, name, email
    payload = {
        'user': {
            'type': user_type,
            'name': user_name,
            'email': user_email,
            user_attribute_type: user_attribute_value
        }
    }

    # a message for the terminal/logs
    if user_attribute_type == 'job_title' and job_title_empty:
        print(f"Removed {user_attribute_type} for {user_name}")
    else:
        print(f"Updating user {user_name} with the new {user_attribute_type} of {user_attribute_value}")

    requests.put("https://api.pagerduty.com/users/" + user_id, headers=header, json=payload)

def run_custom_dataframe_checks(df):
    # basic checks based on the number of columns in the csv file
    if len(df.columns) > 1:
        if not df.columns[0] == 'email':
            print(f"The first header in the csv file must be email. Exiting now.")
            sys.exit()
        else:
            # list of editable user object attributes (supported by this script)
            user_object_attributes = {'name', 'email', 'time_zone', 'role', 'description', 'job_title'}
            for df_cols in df.columns:
                if df_cols not in user_object_attributes:
                    print(f"Column header \"{df_cols}\" not found in valid user object attributes. Column headers should be one of these - {user_object_attributes}")
                    sys.exit()

                # need to check the possible roles in the dataframe - https://support.pagerduty.com/docs/advanced-permissions#roles-in-the-rest-api-and-saml
                if df_cols == 'role':
                    invalid_role_found = False
                    for df_row in df.itertuples():
                        if df_row.role not in {'admin', 'read_only_user', 'read_only_limited_user', 'user', 'limited_user', 'observer', 'restricted_access', 'owner', np.nan}:
                            invalid_role_found = True
                            print(f"Invalid role '{df_row.role}' specified for {df_row.email}")

                    if invalid_role_found:
                        print(f"Please fix the invalid roles found in the csv to continue. No change has been made to the account.")
                        sys.exit()

    else:
        print(f"Number of columns is too less to run the script. Exiting now.")
        sys.exit()

    return df

def main():
    df = run_custom_dataframe_checks(pd.read_csv(args.file_name))

    # fetch a list of all users in the account 
    users_list = fetch_all_users(args.api_key)

    for df_row in df.itertuples():
        user_found = False
        for user in users_list:
            # we have a match
            if df_row.email == user['email']:
                user_found = True
                for df_col_title in df.columns:
                    # debug: 
                    # print(f"DEBUG: User email: {df_row.email}")
                    # print(f"DEBUG: {df_col_title}: {getattr(df_row, df_col_title)}")

                    # check for nan values. nan values mean the field has to be skipped
                    user_attribute_value = None
                    try:
                        user_attribute_value = getattr(df_row, df_col_title)
                        if np.isnan(user_attribute_value):
                            print(f"Empty attribute '{df_col_title}' skipped for user {df_row.email}")
                    except TypeError:
                        # check for duplicate values supplied
                        if user[df_col_title] == user_attribute_value: # we need to skip the update_user_attribute call completely
                            print(f"User {user['name']} already has the attribute '{df_col_title}' set to '{user_attribute_value}'. Nothing to do here. ")
                        else:
                            update_user_attribute(args.api_key, user['id'], user['type'], user['name'], user['email'], df_col_title, user_attribute_value )

        if not user_found:
            print(f"Skipping user with email address \"{df_row.email}\" not found in the account")

if __name__ == "__main__":
    # parse the command line arguments
    parser = argparse.ArgumentParser(description='Modify user object attributes based on the column headers supplied in the csv file. \
        The script supports changing the name, email, time_zone, role, description, job_title.')
    parser.add_argument('-a', '--api-key', required=True, help='global api key from the account')
    parser.add_argument('-f', '--file-name', required=True, help='path of the csv file to be parsed')
    args = parser.parse_args()

    main()