#!/usr/bin/python3
# Modify user object attributes
# Possible user object attributes which can be modified are: name, email, time_zone, role, description, job_title
#
# the script searches the object with the user email address and proceeds to modify the attributes specified in the next column
# the columns should have the headers which are used to identify the column types

import pandas as pd # required to work on the csv files
import numpy as np  # imported just to do the np.nan comparisions
import sys
import json
import requests
import argparse

def fetch_all_users(api_key):
    """
        This function will fetch all the user accounts with their account details. We need to pass a global API key as a required argument
        to this function.

        It returns a Pandas DataFrame.
    """
    print("Fetching all users from the account...")
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

        # fetch the batch of users
        response = json.loads(requests.get('https://api.pagerduty.com/users', headers=header, params=querystring).text)
        more = response['more']
        offset += limit

        users_list.extend(response['users'])

    # convert users list to DataFrame
    users_list_df = pd.DataFrame(users_list)
    print(f"{len(users_list_df)} user records have been fetched successfully.")

    return users_list_df

def update_user_attribute(api_key, user_id, user_type, user_name, user_email, user_attribute_type, user_attribute_value):
    header = {
            'accept': "application/vnd.pagerduty+json;version=2",
            'content-type': "application/json",
            'authorization': "Token token=" + api_key
    }

    # required fields are: type, name, email
    payload = {
        'user': {
            'type': user_type,
            'name': user_name,
            'email': user_email,
            user_attribute_type: user_attribute_value
        }
    }

    # a message for the terminal/logs
    print(f"Updating user {user_name} with the new {user_attribute_type} of {user_attribute_value}")

    requests.put("https://api.pagerduty.com/users/" + user_id, headers=header, json=payload)

def csv_dataframe_checks(csv_df):
    """
        The purpose of this function is to run checks on the CSV file loaded from the disk. There are certain columns which have a value requirement to be in a
        specific format. We run through these values based on their column index and notify the user about any possible invalid values in them. The reason to run
        these checks before we make any changes to the PagerDuty account is to avoid any possible typo's or possible invalid entries.

        For example, the first column of the script should be them email column of the login emails of the user accounts.

        The roles column should only have certain role values, which are - 
            admin, read_only_user, read_only_limited_user, user, limited_user, observer, restricted_access, owner
        
        Similarly, the job_title column has some restrictions. Because this script's purpose is to edit an existing users attributes, we have to supply a job_title
        value between 1..100
    """

    print(f"Running checks on the CSV file - {args.csv_file} ...")

    # minimum number of columns should be 2, first for the email and the minimum next for the attribute that needs changing
    if not len(df.columns) > 1:
        print("Number of columns is too less to run the script. Exiting now.")
        sys.exit()

    # check if the first column of the csv file is the email field
    if not df.columns[0] == 'email':
        print(f"The first header in the csv file must be email. Exiting now.")
        sys.exit()

    # now the first column is email, check for the rest of the columns.
    # set of editable user object attributes (supported by this script). these have to be the column header/indexes in the supplied csv file.
    # the following checks are to ensure that the column indexes match the field names from the api
    user_object_attributes = {'name', 'email', 'time_zone', 'role', 'description', 'job_title'}

    # go through all the columns in the csv file. skip the first one because it is email. check has been run on the first column index above
    for col_index in csv_df.columns[1:]:
        if col_index not in user_object_attributes:
            print(f"Column header \"{col_index}\" is not a valid user object attributes. Column headers should be one of these - {user_object_attributes}")
            print("Fix the column headers to continue...")
            sys.exit()

        # role is a special column index which if supplied, should have certain values in the column
        # check the possible roles in the dataframe - https://support.pagerduty.com/docs/advanced-permissions#roles-in-the-rest-api-and-saml
        if col_index == 'role':

            # iterate through the role column DataFrame to find any invalid roles.
            # if the role field is specified and is empty for some reason in a row, then we should skip setting it
            valid_roles = {'admin', 'read_only_user', 'read_only_limited_user', 'user', 'limited_user', 'observer', 'restricted_access', 'owner', None}
            invalid_role_found = False

            # point out all the occurences of invalid roles in the csv's role column
            for df_row in csv_df.itertuples():

                if df_row.role not in valid_roles:
                    invalid_role_found = True
                    print(f"An invalid role of '{df_row.role}' specified for user - {df_row.email}")

            if invalid_role_found:
                print("Invalid entries have been found in the 'role' column. Fix them in the csv file to continue.")
                sys.exit()

        # job_title when supplied will mean one of the 2 possible cases - 
        # 1. add job_title to an existing user, or 2. remove job_title for an existing user. 
        # when removing, in case 2, ensure that you supply an empty string. this field does not take a null/None argument
        if col_index == 'job_title':

            invalid_job_title_found = False

            # parse thru all the occurences of invalid roles in the csv's role column
            for df_row in csv_df.itertuples():

                # set the job_title to an empty one space string if no job_title is specified. it is not an invalid role.
                # this would happen when the user wishes to remove the existing job_title for any reason
                if df_row.job_title is None:
                    print(f"The script will be removing the job_title for the user - {df_row.email}")
                    df_row.job_title = ' '

                # the job_title has exceeded the max value of the job_title
                if len(str(df_row.job_title)) > 100:
                    print(f"The max length of the 'job_title' column has exceeded for user - {df_row.email}")
                    invalid_job_title_found = True

            if invalid_job_title_found:
                print("Invalid entries have been found in the 'job_title' column. Fix them in the csv file to continue.")
                sys.exit()

    print("Checks completed on the CSV file.")
    return csv_df

def run_checks_and_update(csv_df_columns, csv_df_row, user_data):
    for csv_df_column_index in csv_df_columns:
        # check for nan values. nan values mean the field has to be skipped
        user_attribute_value = None
        try:
            user_attribute_value = getattr(csv_df_row, csv_df_column_index)
            if np.isnan(user_attribute_value): 
                print(f"Empty attribute '{csv_df_column_index}' skipped for user {csv_df_row.email}")
        except TypeError:
            # check for any duplicate values supplied in the csv. we can save on processing if the value supplied in the csv is the same as an existing user attribute
            if user_data[csv_df_column_index] == user_attribute_value: # we need to skip the update_user_attribute call completely
                print(f"User {user_data['name']} already has the attribute '{csv_df_column_index}' set to '{user_attribute_value}'. Skipping... ")

            elif csv_df_column_index == 'job_title':    # this one is specifically for the job_title since it can only be between 1..100
                if len(user_attribute_value.strip()) == 0:
                    print(f"Removing 'job_title' for {user_data['name']}...")
                    user_attribute_value = ' '          # it can only be between 1..100. Hack is to pass an empty string
                    update_user_attribute(args.api_key, user_data['id'], user_data['type'], user_data['name'], user_data['email'], csv_df_column_index, user_attribute_value)
                elif len(user_attribute_value.strip() > 100):
                    print("The 'job_title' field has more than 100 characters in it which is more than the maximum value it can hold.")

            else:
                print(f"Updating user '{user_data['name']}' with the new '{csv_df_column_index}' of '{user_attribute_value}'...")
                update_user_attribute(args.api_key, user_data['id'], user_data['type'], user_data['name'], user_data['email'], csv_df_column_index, user_attribute_value)

def main():
    # read the csv file from the disk to a Pandas DataFrame
    csv_df = csv_dataframe_checks(pd.read_csv(args.file_name))

    # fetch a list of all users in the account to a Pandas DataFrame
    users_list_df = fetch_all_users(args.api_key)

    sys.exit()

    for csv_row in csv_df.itertuples():
        user_found = False
        for user_data in users_list_df.itertuples():
            if user_data.email == csv_row.email:
                user_found = True
                update_user_attribute(args.api_key, user_data['id'], user_data['type'], user_data['name'], user_data['email'], csv_df_column_index, user_attribute_value) if run_dataframe_checks(csv_df.columns, csv_row, user_data)

        if not user_found:
            print(f"Skipping user with email address \"{csv_row.email}\" not found in the account")

if __name__ == "__main__":
    # parse the command line arguments
    parser = argparse.ArgumentParser(description='Modify user object attributes based on the column headers supplied in the csv file. \
        The script supports changing the name, email, time_zone, role, description, job_title.')
    parser.add_argument('-a', '--api-key', required=True, help='global api key from the account')
    parser.add_argument('-f', '--file-name', required=True, help='path of the csv file to be parsed')
    args = parser.parse_args()

    main()