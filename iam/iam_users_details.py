import boto3
import os
import sys
import csv
import pandas as pd
from datetime import datetime, timezone

# env=str(sys.argv[1])
# os.environ['AWS_PROFILE'] = env

session = boto3.Session()
profiles = session.available_profiles

users_list = []

for profile in profiles: 

    profile_session = boto3.session.Session(profile_name=profile)

    iam = profile_session.client('iam')
    paginator = iam.get_paginator('list_users')
    iam_users_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
    # print (ia m_users_paginator)

    for page in iam_users_paginator:

        for user in page['Users']:
            
            print(user['UserName'])
            user_dict = {}
            user_dict['UserName'] = user['UserName']
            user_dict['ARN'] = user['Arn']
            # user_dict['UserId'] = user['UserId']
            user_dict['CreatedDate'] = user['CreateDate']

            # Describe User 
            user_info = iam.get_user(UserName=user['UserName'])
            
            if user_info.get('User').get('Tags') and user_info.get('User').get('PasswordLastUsed'):
                user_dict['Tags'] = user_info['User']['Tags']
                user_dict['PasswordLastUsed']=user_info['User']['PasswordLastUsed']
            elif user_info.get('User').get('Tags'):
                user_dict['Tags'] = user_info['User']['Tags']
                user_dict['PasswordLastUsed']='--'
            else:
                user_dict['Tags'] = '--'
                user_dict['PasswordLastUsed']='--'
            
            access_keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
            access_key_list=[]
            last_activity=""
            for access_key in access_keys:
                
                if access_key['Status'] == 'Active':

                    access_key_list.append(access_key['AccessKeyId'])
                    
                    last_used = iam.get_access_key_last_used(AccessKeyId=access_key['AccessKeyId'])
                    if 'LastUsedDate' in last_used['AccessKeyLastUsed']:
                        
                        last_used_date = last_used['AccessKeyLastUsed']['LastUsedDate'].replace(tzinfo=None)
                        last_activity = last_used_date
                        user_dict['LastActivity'] = last_activity

                        age = datetime.now(last_used_date.tzinfo) - last_used_date
                        user_dict['LastUsedAge'] = (datetime.now(last_used_date.tzinfo) - last_used_date).days

                    else:
                        user_dict['LastUsedAge'] = 'N/A'
                        last_activity = 'N/A'
                        user_dict['LastActivity'] = last_activity

            user_dict['ActiveAccessKeys'] = access_key_list

            print('---')
            users_list.append(user_dict)

df = pd.DataFrame(users_list)
print(df)
filename="iam_users" + ".csv"
df.to_csv(filename)