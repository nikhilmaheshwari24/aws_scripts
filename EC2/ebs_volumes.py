import boto3
from datetime import datetime, timezone
import pandas as pd
import os

# Set AWS profile
os.environ['AWS_PROFILE'] = "<profile-name>"

def calculate_age(create_date):
    """
    Calculate the age of a volume based on its creation date.

    Args:
    create_date (datetime): The creation date of the volume.

    Returns:
    int: The age of the volume in days.
    """
    create_date = datetime.fromisoformat(str(create_date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

# Regions
regions = ['us-east-2']

volumes_info = []

for region in regions:
    ec2_client = boto3.client('ec2', region_name=region)
    paginator = ec2_client.get_paginator('describe_volumes')
    volumes_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

    for page in volumes_paginator:
        for volume in page['Volumes']:
            volume_details = {}

            # Extracting Volume Name
            if 'Tags' in volume:
                for tag in volume['Tags']:
                    if 'Name' == tag['Key']:
                        volume_details['Name'] = tag['Value']
                    else:
                        continue
            else:
                volume_details['Name'] = ""

            volume_details['CreateTime'] = volume['CreateTime']
            volume_details['VolumeAge'] = calculate_age(volume['CreateTime'])
            volume_details['VolumeID'] = volume['VolumeId']
            volume_details['State'] = volume['State']
            volume_details['VolumeType'] = volume['VolumeType']
            volume_details['AvailabilityZone'] = volume['AvailabilityZone']
            volume_details['Size'] = volume['Size']
            volume_details['Encryption'] = volume['Encrypted']

            if 'SnapshotId' in volume:
                volume_details['SnapshotId'] = volume['SnapshotId']
            else:
                volume_details['SnapshotId'] = ""

            volume_details['Iops'] = volume['Iops']

            if 'Throughput' in volume:
                volume_details['Throughput'] = volume['Throughput']
            else:
                volume_details['Throughput'] = ""

            try:
                tags = volume['Tags']
                tag_list = [f"{tag['Key']}: {tag['Value']}" for tag in tags]
                volume_details['Tags'] = '\n'.join(tag_list)
            except:
                volume_details['Tags'] = ""

            volumes_info.append(volume_details)

            print(volume['VolumeId'], " <> ")

dataframe = pd.DataFrame(volumes_info)
filename = "EBS_Volumes.csv"
dataframe.to_csv(filename, index=False)