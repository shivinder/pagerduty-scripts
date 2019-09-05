#!/usr/bin/env python3
# REST API Guide: https://api-reference.pagerduty.com
# Just needs the API Token from the Account Owner to run
# TODO: exception handling when no/invalid api_token is passed
#       minor tweaks :)

import requests
import json

# account definitions
api_token = 'api_token'
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
total_scanned, total_phone_updates, total_sms_updates, total_notification_updates = 0, 0, 0, 0

# define global lists to store the self urls for contact methods defined in user data
phone_url_list, sms_url_list, notification_url_list = [], [], []

while True:
    params = {'include[]': 'contact_methods', 'limit': limit, 'offset': offset}

    # Get the list of users from PD with their contact methods and convert it to JSON
    users_list = json.loads(requests.get(url, params=params, headers=header).text)

    # contact methods
    for user in users_list['users']:
        # update the total count
        total_scanned+=1
        
        # working example: print(users_list['users'][0]['contact_methods'][0]['address'])
        uid = user['id']

        # reset the arrays for the current user
        current_phone_url_list, current_sms_url_list = [], []
        
        # this loop handles multiple contact methods, if any, for one user
        # we have to get the phone and sms self url's, 
        # save them to a local list then append this list to the global list to be deleted later
        for contact_method in user['contact_methods']: 
            # handle the phone contacts here
            if contact_method['type'] == 'phone_contact_method':
                total_phone_updates+=1

                # fetch the required url
                phone_url = contact_method['self']
                current_phone_url_list.append(phone_url)
            elif contact_method['type'] == 'sms_contact_method':
                total_sms_updates+=1

                # fetch the required url
                sms_url = contact_method['self']
                current_sms_url_list.append(sms_url)
        
        # for notification_rule in user['notification_rules']:
        #     # we will have to go through all the notification rules to verify their use
        #     # the phone number is in their summary field, extract the text from there
        #     # iterate the phone numbers first
        #     contact_method_id = notification_rule['summary'][-7:]
        #     for phone_list_element in current_phone_url_list:
        #         if phone_list_element[-7:] == contact_method_id:
        #             total_notification_updates+=1
        #             notification_url_list.append(notification_rule['self'])
            
        #     # iterate the sms numbers second
        #     for sms_list_element in current_sms_url_list:
        #         if sms_list_element[-7:] == contact_method_id:
        #             total_notification_updates+=1
        #             notification_url_list.append(notification_rule['self'])

        # join the local url lists to global url lists
        phone_url_list += current_phone_url_list
        sms_url_list += current_sms_url_list

    # condition to break out of infinite while loop
    if users_list['more'] == True:
        offset+=limit
    else:
        break

# run the delete requests for the URLs collected above
if phone_url_list:
    for phone_url in phone_url_list:
        print('deleting phone URL: {}'.format(phone_url))
        phone_url_delete_response = requests.delete(phone_url, headers=header)
        print(str(phone_url_delete_response.status_code) + ' - ' + phone_url_delete_response.text)
else:
    print('No Phone numbers found on account on any user')

if sms_url_list:
    for sms_url in sms_url_list:
        print('deleting SMS URL: {}'.format(sms_url))
        sms_url_delete_response = requests.delete(sms_url, headers=header)
        print(str(sms_url_delete_response.status_code) + ' - ' + sms_url_delete_response.text)
else:
    print('No SMS numbers found on account on any account')

# if notification_url_list:
#     for notification_rule in notification_url_list:
#         print('deleting notification rule: {}'.format(notification_rule))
#         notification_url_delete_response = requests.delete(notification_rule, headers=header)
#         print(str(notification_url_delete_response.status_code) + ' - ' +  notification_url_delete_response.text)
# else:
#     print('No Notification URLs found on account')

# print come fancy stats on terminal
print('total users scanned: {}\ntotal phone notifications deleted: {}\ntotal sms notifications deleted: {} \
    \n'.format(total_scanned,total_phone_updates,total_sms_updates))
print('script run completed')