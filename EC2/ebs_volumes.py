import boto3
import os
import sys
import csv
from datetime import datetime, timezone
import pandas as pd

def age(date):
    create_date = datetime.fromisoformat(str(date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

# regions
regions=['us-east-2']

volumes_list=[]

for region in regions:

    ebs_volumes = boto3.client('ec2', region_name=region)
    paginator = ebs_volumes.get_paginator('describe_volumes')
    volumes_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

    for page in volumes_paginator:

        for volume in page['Volumes']:
            
            print(volume['VolumeId']," <> ")

            volume_dict={}

            # Extracting Volume Name
            if 'Tags' in volume:
                for tag in volume['Tags']:
                    if 'Name' == tag['Key']:
                        volume_dict['Name'] = tag['Value']
                    else: 
                        continue
            else:
               volume_dict['Name'] = ""

            volume_dict['CreateTime'] = volume['CreateTime']
            volume_dict['VolumeAge'] = age(volume['CreateTime'])
            volume_dict['VolumeID'] = volume['VolumeId']
            volume_dict['State'] = volume['State']
            volume_dict['VolumeType'] = volume['VolumeType']
            volume_dict['AvailabilityZone'] = volume['AvailabilityZone']
            volume_dict['Size'] = volume['Size']
            volume_dict['Encryption'] = volume['Encrypted']
            
            if 'SnapshotId' in volume:
                volume_dict['SnapshotId'] = volume['SnapshotId']
            else:
                volume_dict['SnapshotId'] = ""

            volume_dict['Iops'] = volume['Iops']

            if 'Throughput' in volume:
                volume_dict['Throughput'] = volume['Throughput']
            else:
                 volume_dict['Throughput'] = ""

            # volume_dict['FastRestored'] = volume['FastRestored']
            # volume_dict['MultiAttachEnabled'] = volume['MultiAttachEnabled']

            volumes_list.append(volume_dict)
            
dataframe = pd.DataFrame(volumes_list)
filename = "EBS_Volumes.csv"
dataframe.to_csv(filename)
