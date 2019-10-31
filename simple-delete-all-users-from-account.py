#!/usr/bin/python3

# This script will delete all the users from the account. Will have to follow these steps in order:
# 1. Get a list of all the incidents on the account - resolve them
# 2. Get a list of all the teams on the account - delete them
# 3. Get a list of all the EP's on the account - delete them
# 4. Get a list of all the Schedules on the account - delete them
# 5. Get a list of all the users on the account - delete them

import requests
import argparse

