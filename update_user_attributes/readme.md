## Description

Use this script to modify the User object attributes via PagerDuty public API. The possible user attributes which can be modified at the moment are:

- name
- email
- job_title
- description
- role
- time_zone

## Installation

It is recommended to use python's virtual environments. You may create one with the following command

```
python3 -m venv env
```

Next you need to switch to this new virtual environment

```
. .env/bin/activate
```

Now we need to install the required libraries to run this script. The list of libraries is in the accompanying file `requirements.txt` and you may install them in one go, if you have access to `pip` using

```
pip install -r requirements.txt
```

## Usage

The general syntax of the script is

```
./update_user_attributes.py --api-key <global_api_key> --file <path_to_csv_file>
```

## CSV file format

Headers - The script expects the CSV file to have headers which correspond to the user attributes that need changing. 

The first column of the CSV file must have the user login email addresses.

The subsequent columns of the csv will be the user attributes that need to be changed. More explanation is in the examples below.

Example to change just the `job_title` field:

```
email,job_title
user1@example.com,Telecom Manager
user2@example.com,Field Officer
```

Example to change the `job_title` and the `description` field. Last row is missing description.

```
email,job_title,description
user1@example.com,Telecom Manager,Manages the Telecom Team
user2@example.com,Field Officer,Fixes the actual problem in cables
yser3@example.com,CTO,
```

Email addresses can also be changed. You will need to mention the old/exiting email address in the first column, which is a requirement, and the new email address in any subsequent columns, with the same title `email`. Check example below:

```
email,email
user1@example.com,new_user1@example.com
user2@example.com,new_user2@example.com
```

*Important points to consider while drafting the CSV file*

- column data may be missed but the field seperator is necessary. for example, you may have a row which is `user99@example.com,,I am a test`
- Possible user object field names, which should be the CSV headers are - `name`, `email`, `job_title`, `description`, `role`, `time_zone`. The script will point out any errors in naming these headers and exit. No change will be made to the account.

## Pending

- check if the role supplied is a valid role, exit if an invalid role is found with no changes to the account
- changes to the time zone part has no error checks. Will fail if incorrect time zone data is supplied