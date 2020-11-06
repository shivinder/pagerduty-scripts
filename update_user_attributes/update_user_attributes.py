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

    print(f"\nBeginning to run checks on the supplied CSV file - '{args.file_name}' ...")

    # replace NaN values or this missing values in the DataFrame with None
    csv_df = csv_df.where(csv_df.notnull(), None)

    # minimum number of columns should be 2, first for the email and the minimum next for the attribute that needs changing
    if not len(csv_df.columns) > 1:
        print("Number of columns is too less to run the script. Exiting now.")
        sys.exit()

    # check if the first column of the csv file is the email field
    if not csv_df.columns[0] == 'email':
        print(f"The first header in the csv file must be email. Please read the supplied documentation. Exiting now.")
        sys.exit()

    # now the first column is email, check for the rest of the columns.
    # set of editable user object attributes (supported by this script). these have to be the column header/indexes in the supplied csv file.
    # the following checks are to ensure that the column indexes match the field names from the api
    user_object_attributes = {'name', 'email', 'time_zone', 'role', 'description', 'job_title'}

    # we will use these flag variables to display error messages after the column checks have been completed.
    invalid_column_index_found, invalid_role_found, invalid_job_title_found = False, False, False

    # go through all the columns in the csv file. skip the first one because it is email. check has been run on the first column index above
    for col_index in csv_df.columns[1:]:
        if col_index not in user_object_attributes:
            invalid_column_index_found = True
            print(f"Column header \"{col_index}\" is not a valid user object attributes.")

    # exit here if column indexes have invalid values
    if invalid_column_index_found:
        print(f"Invalid entries have been found in the 'job_title' column. Should be one of these - {user_object_attributes}. Fix them in the csv file to continue.")
        sys.exit()

    for col_index in csv_df.columns[1:]:
        # role is a special column index which if supplied, should have certain values in the column
        # check the possible roles in the dataframe - https://support.pagerduty.com/docs/advanced-permissions#roles-in-the-rest-api-and-saml
        if col_index == 'role':

            # iterate through the role column DataFrame to find any invalid roles.
            # if the role field is specified and is empty for some reason in a row, then it's value would be set to None and it would be skipped in the later checks
            valid_roles = {'admin', 'read_only_user', 'read_only_limited_user', 'user', 'limited_user', 'observer', 'restricted_access', 'owner', None}

            # point out all the occurences of invalid roles in the csv's role column
            for csv_df_row in csv_df.itertuples():

                if csv_df_row.role not in valid_roles:
                    invalid_role_found = True
                    print(f"An invalid role of '{csv_df_row.role}' specified for user - {csv_df_row.email}")

        # job_title when supplied will mean one of the 2 possible cases - 
        # 1. add job_title to an existing user, or 2. remove job_title for an existing user. 
        # when removing, in case 2, ensure that you supply an empty string. this field does not take a null/None argument
        if col_index == 'job_title':

            # set the job_title to an empty one space string if no job_title is specified. it is not an invalid role.
            # this would happen when the user wishes to remove the existing job_title for any reason
            csv_df['job_title'] = csv_df['job_title'].replace([None], ' ')

            # parse thru all the occurences of job_titles in the csv to check their length, which should be <= 100
            for csv_df_row in csv_df.itertuples():

                # the job_title has exceeded the max value of the job_title
                if len(str(csv_df_row.job_title)) > 100:
                    print(f"The max length of the 'job_title' column has exceeded for user - {csv_df_row.email}")
                    invalid_job_title_found = True

    # this is where we display the error message before exiting the script. this way we are able to display the errors for all
    # the columns checked above for the users convenience. they can correct them in one go rather than running the script again just to find more invalid values
    if invalid_role_found or invalid_job_title_found:
        if invalid_role_found:
            print("Invalid entries have been found in the 'role' column. Fix them in the csv file to continue.")

        if invalid_job_title_found:
            print("Invalid entries have been found in the 'job_title' column. Fix them in the csv file to continue.")

        sys.exit()

    print("Checks completed on the CSV file.\n")
    return csv_df

def fetch_all_users(session):
    """
        This function will fetch all the user accounts with their account details. We need to pass a global API key as a required argument
        to this function.

        It returns a Pandas DataFrame.
    """
    print("\nFetching users list from the PagerDuty account...")
    users_list = []

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
        users_list_batch = json.loads(session.get('https://api.pagerduty.com/users', params=querystring).text)
        more = users_list_batch['more']
        offset += limit

        users_list.extend(users_list_batch['users'])

    # convert users list to DataFrame
    users_list_df = pd.DataFrame(users_list)
    print(f"{len(users_list_df)} user records have been fetched successfully from the PagerDuty account.\n")

    return users_list_df

def update_user_attribute(session, user_id, payload):
    """
        This function will perform the actual updating in the PagerDuty account.
    """

    response = session.put("https://api.pagerduty.com/users/" + user_id, json=payload)

    if response.ok:
        print("User updated successfully")
    else:
        print(f"Problem encountered while updating user - {response.text}")

def main():
    # create a requests session
    session = requests.Session()

    # and set the session headers
    session.headers.update({
        'accept': "application/vnd.pagerduty+json;version=2",
        'content-type': "application/json",
        'authorization': "Token token=" + args.api_key
    })

    # read the csv file from the disk to a Pandas DataFrame
    csv_df = csv_dataframe_checks(pd.read_csv(args.file_name))

    # fetch a list of all users in the account to a Pandas DataFrame
    pd_users_df = fetch_all_users(session)

    # store the csv column indexes in a list just for faster operation
    csv_column_indexes = list(csv_df.columns)

    # main logic \m/
    print("\nUpdating the PagerDuty account now...\n")
    # parse through one csv row at a time and compare it to the user accounts fetched from the PagerDuty account
    for csv_row in csv_df.itertuples():

        # flag variable used to identify if the user email address from the csv file has been found in the user list fetched from the PagerDuty account
        user_found = False

        # search for the csv email address in the users list fetched from the PagerDuty account
        for pd_user_row in pd_users_df.itertuples():

            # the email address supplied in the csv maps to a user in PagerDuty users list. we have a match!
            if pd_user_row.email == csv_row.email:
                print(f"Email address '{csv_row.email}' maps to user '{pd_user_row.name}' with the ID '{pd_user_row.id}' in the PagerDuty account.'")
                user_found = True

                # after we have a confirmed match, this is where we will be forming the payload
                # before running the update user attribute, we check if the supplied value isn't None to save time on making unnecessary function calls

                # define the default payload for this user. the required fields are type, name and email.
                payload = {
                    'user': {
                        'type': pd_user_row.type,
                        'name': pd_user_row.name,
                        'email': pd_user_row.email
                    }
                }

                # define a variable to keep a track of the payload if it is modified in the following checks in the loop
                payload_modified = False
                payload_attribute_names, payload_attribute_values = [], []

                # go through all the csv indexes. skip the first one which is email
                for csv_column_index in csv_column_indexes[1:]:

                    # fetch the value from the PagerDuty user object to see its worth
                    user_attribute_value = getattr(pd_user_row, csv_column_index)

                    if user_attribute_value == getattr(pd_user_row, csv_column_index):
                        # the supplied value in the csv is the same as the existing attribute value in the account
                        print(f"Skipping attribute update - user '{pd_user_row.name}' has the '{csv_column_index}' attribute already set to '{user_attribute_value}'.")
                    elif user_attribute_value is None:
                        # no value has been supplied in the csv 
                        print(f"Skipping attribute update - user '{pd_user_row.name}' has been not been supplied with any value for '{csv_column_index}'.")
                    else:
                        print("Payload modified!")
                        payload_modified = True
                        # add the attributes and its value to the payload
                        payload['user'][csv_column_index] = user_attribute_value
                        # modify the message to print on terminal
                        payload_attribute_names.append(csv_column_index)
                        payload_attribute_values.append(user_attribute_value)
                        print(payload)

                if payload_modified:
                    print(f"Attempting to update following attributes for user '{pd_user_row.name}' - '{payload_attribute_names}' with the values '{payload_attribute_values}' ...")
                    sys.exit()
                    update_user_attribute(session, pd_user_row.id, payload)

                # this user is done. no need to parse other users from the pd_users_df. move on to the next one from the csv
                break

        if not user_found:
            print(f"Skipping csv row with email address '{csv_row.email}'. Reason - Could not find a user mapped to '{csv_row.email}' in the PagerDuty account")
    
    print("\nScript execution finished.\n")

if __name__ == "__main__":
    # parse the command line arguments
    parser = argparse.ArgumentParser(description='Modify user object attributes based on the column headers supplied in the csv file. \
        The script supports changing the name, email, time_zone, role, description, job_title.')
    parser.add_argument('-a', '--api-key', required=True, help='global api key from the account')
    parser.add_argument('-f', '--file-name', required=True, help='path of the csv file to be parsed')
    args = parser.parse_args()

    main()