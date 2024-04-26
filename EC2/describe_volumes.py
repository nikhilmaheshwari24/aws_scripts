import boto3
from datetime import datetime, timezone
import pandas as pd
import os

# Set AWS profile
os.environ['AWS_PROFILE'] = ''

def calculate_age(create_date):
    # Function to calculate age of a volume based on its create time
    create_date = datetime.fromisoformat(str(create_date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

# Regions
regions = ['us-east-2']

volumes_list = []

for region in regions:
    # Create EC2 client for the specified region
    ebs_volumes = boto3.client('ec2', region_name=region)
    paginator = ebs_volumes.get_paginator('describe_volumes')
    volumes_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})

    for page in volumes_paginator:
        for volume in page['Volumes']:
            volume_dict = {}
            # Extracting Volume Name from Tags
            if 'Tags' in volume:
                for tag in volume['Tags']:
                    if 'Name' == tag['Key']:
                        volume_dict['Name'] = tag['Value']
                    else:
                        continue
            else:
                volume_dict['Name'] = ""
            # CreateTime of the volume
            volume_dict['CreateTime'] = volume['CreateTime']
            # Calculate VolumeAge
            volume_dict['VolumeAge'] = calculate_age(volume['CreateTime'])
            # VolumeID
            volume_dict['VolumeID'] = volume['VolumeId']
            # VolumeState
            volume_dict['State'] = volume['State']
            # VolumeType
            volume_dict['VolumeType'] = volume['VolumeType']
            # AvailabilityZone
            volume_dict['AvailabilityZone'] = volume['AvailabilityZone']
            # VolumeSize
            volume_dict['Size'] = volume['Size']
            # VolumeEncryption
            volume_dict['Encryption'] = volume['Encrypted']
            # VolumeKMSKeyID
            volume_dict['KmsKeyId'] = volume.get('KmsKeyId',None)
            # VolumeSnapshotID
            volume_dict['SnapshotId'] = volume.get('SnapshotId', "")
            # VolumeIOPS
            volume_dict['Iops'] = volume['Iops']
            # VolumeThroughput
            volume_dict['Throughput'] = volume.get('Throughput', "")
            # VolumeMultiAttachEnabled
            volume_dict['MultiAttachEnabled'] = volume.get('MultiAttachEnabled', None)
            # VolumeFastRestored
            volume_dict['FastRestored'] = volume.get('FastRestored', None)
            # VolumeTags
            try:
                tags = volume['Tags']
                tag_list = [f"{tag['Key']}: {tag['Value']}" for tag in tags]
                volume_dict['Tags'] = '\n'.join(tag_list)
            except:
                volume_dict['Tags'] = ""
            volumes_list.append(volume_dict)
            # Print VolumeId for monitoring
            print(volume['VolumeId'], " <> ")

# Create a DataFrame from the list of volume dictionaries
dataframe = pd.DataFrame(volumes_list)

# Write the DataFrame to a CSV file
filename = "EBS_Volumes.csv"
dataframe.to_csv(filename, index=False)
