import boto3
import os
import sys
import csv
import pandas as pd

# env=str(sys.argv[1])
# os.environ['AWS_PROFILE'] = env

regions = ['us-east-1','ap-southeast-1','ap-south-1']

session = boto3.Session()
profiles = session.available_profiles

instance_list=[]

for profile in profiles:

    for region in regions:

        profile_session = boto3.session.Session(profile_name=profile)

        acc_info = profile_session.client('sts')
        acc_sts = acc_info.get_caller_identity()

        acc_no = acc_sts['Account']

        ec2 = profile_session.client('ec2', region_name=region)
        paginator = ec2.get_paginator('describe_instances')
        ec2_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

        for page in ec2_paginator:
            
            for reservation in page['Reservations']:
                
                for instance in reservation['Instances']:

                    instance_dict={}

                    instance_name = '-'

                    if instance.get('Tags'):

                    # Check if the instance has the specified tag
                        flag = False
                        for tag in instance['Tags']:
                            if tag['Key'] == "aws:autoscaling:groupName":
                                flag = True
                                break
                            if tag['Key'] == "Name":
                                instance_name = tag['Value']
                                

                    # If the instance does not have the specified tag, print its ID
                        if not flag:
                            instance_dict['Account'] = acc_no
                            instance_dict['Region'] = region
                            instance_dict['InstanceName'] = instance_name
                            instance_dict['InstanceId'] = instance['InstanceId']
                            print (acc_no,region,instance_name,instance['InstanceId'])
                            instance_list.append(instance_dict)

df = pd.DataFrame(instance_list)
print(df)
filename = 'Standalone_Instances' + '.csv'
df.to_csv(filename)