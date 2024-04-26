import boto3
import os
import sys
import csv
import pandas as pd
from datetime import datetime, timezone

# env=str(sys.argv[1])
# os.environ['AWS_PROFILE'] = env

# Create a session using default credentials
session = boto3.Session()

# Get available profiles from the session
profiles = session.available_profiles

# List to store IAM user information
users_list = []

# Iterate over each profile
for profile in profiles: 
    # Create a session with the current profile
    profile_session = boto3.session.Session(profile_name=profile)

    # Create an IAM client
    iam = profile_session.client('iam')

    # Use a paginator to retrieve IAM users
    paginator = iam.get_paginator('list_users')
    iam_users_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

    # Iterate over each page of IAM users
    for page in iam_users_paginator:
        # Iterate over each IAM user
        for user in page['Users']:
            # Print the username
            print(user['UserName'])
            # Create a dictionary to store user information
            user_dict = {}
            user_dict['UserName'] = user['UserName']
            user_dict['ARN'] = user['Arn']
            user_dict['CreatedDate'] = user['CreateDate']

            # Retrieve additional user information
            user_info = iam.get_user(UserName=user['UserName'])

            if user_info.get('User').get('Tags') and user_info.get('User').get('PasswordLastUsed'):
                user_dict['Tags'] = user_info['User']['Tags']
                user_dict['PasswordLastUsed'] = user_info['User']['PasswordLastUsed']
            elif user_info.get('User').get('Tags'):
                user_dict['Tags'] = user_info['User']['Tags']
                user_dict['PasswordLastUsed'] = '--'
            else:
                user_dict['Tags'] = '--'
                user_dict['PasswordLastUsed'] = '--'

            # Retrieve access keys for the user
            access_keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
            access_key_list = []
            last_activity = ""
            for access_key in access_keys:
                if access_key['Status'] == 'Active':
                    access_key_list.append(access_key['AccessKeyId'])

                    # Retrieve the last used information for the access key
                    last_used = iam.get_access_key_last_used(AccessKeyId=access_key['AccessKeyId'])
                    if 'LastUsedDate' in last_used['AccessKeyLastUsed']:
                        last_used_date = last_used['AccessKeyLastUsed']['LastUsedDate'].replace(tzinfo=None)
                        last_activity = last_used_date
                        user_dict['LastActivity'] = last_activity

                        # Calculate the age of the last used date
                        age = datetime.now(last_used_date.tzinfo) - last_used_date
                        user_dict['LastUsedAge'] = age.days
                    else:
                        user_dict['LastUsedAge'] = 'N/A'
                        last_activity = 'N/A'
                        user_dict['LastActivity'] = last_activity

            user_dict['ActiveAccessKeys'] = access_key_list

            print('---')
            # Append the user dictionary to the list
            users_list.append(user_dict)

# Create a DataFrame from the list
df = pd.DataFrame(users_list)

# Print the DataFrame
print(df)

# Export the DataFrame to a CSV file
filename = 'iam_users.csv'
df.to_csv(filename)
