import boto3
import os
import sys
import csv
import pandas as pd

# os.environ['AWS_PROFILE'] = env

regions = ['us-east-1', 'ap-southeast-1', 'ap-south-1']

# Create a session using default credentials
session = boto3.Session()

# Get available profiles from the session
profiles = session.available_profiles

# List to store standalone instance information
instance_list = []

# Iterate over each profile
for profile in profiles:
    # Iterate over each region
    for region in regions:
        # Create a session with the current profile
        profile_session = boto3.session.Session(profile_name=profile)
        
        # Retrieve AWS account information
        acc_info = profile_session.client('sts')
        acc_sts = acc_info.get_caller_identity()
        acc_no = acc_sts['Account']
        
        # Create an EC2 client for the region
        ec2 = profile_session.client('ec2', region_name=region)
        
        # Use a paginator to retrieve instances
        paginator = ec2.get_paginator('describe_instances')
        ec2_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
        
        # Iterate over each page of instances
        for page in ec2_paginator:
            # Iterate over each reservation
            for reservation in page['Reservations']:
                # Iterate over each instance
                for instance in reservation['Instances']:
                    instance_dict = {}
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
                                
                        # If the instance does not have the specified tag, store its information
                        if not flag:
                            instance_dict['Account'] = acc_no
                            instance_dict['Region'] = region
                            instance_dict['InstanceName'] = instance_name
                            instance_dict['InstanceId'] = instance['InstanceId']
                            print(acc_no, region, instance_name, instance['InstanceId'])
                            instance_list.append(instance_dict)

# Create a DataFrame from the list
df = pd.DataFrame(instance_list)

# Export the DataFrame to a CSV file
filename = 'Standalone_Instances.csv'
df.to_csv(filename, Index=False)
