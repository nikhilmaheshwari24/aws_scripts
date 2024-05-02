import boto3
import os
import pandas as pd
from datetime import datetime, timezone

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ""

# Define AWS regions to search for RDS snapshots
regions = ['us-east-2']

snapshots_list = []

def snapshot_tags(snapshot_tags_list):

    # Initialize an empty list to store tags
    tag_list = []
    
    # Process each tag and store it in the list
    for tag in snapshot_tags_list:
        key = tag['Key']
        value = tag['Value']
        tag_list.append(f"{key}: {value}")

    # Return the concatenated tags if tags are present
    if tag_list:
        return '\n'.join(tag_list)
    else:
        return "No Tags Available"

def calculate_age(create_date):
    create_date = datetime.fromisoformat(str(create_date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

for region in regions:

    ec2_client = boto3.client('ec2',region_name=region)
    paginator = ec2_client.get_paginator('describe_snapshots')
    ec2_paginator = paginator.paginate(PaginationConfig={'PageSize': 100},OwnerIds=['self'])

    for page in ec2_paginator:

        for snapshot in page['Snapshots']:
                
            snapshot_dict = {}
            snapshot_dict['DataEncryptionKeyId'] = snapshot.get('DataEncryptionKeyId', None)
            snapshot_dict['Description'] = snapshot['Description']
            snapshot_dict['Encrypted'] = snapshot['Encrypted']
            snapshot_dict['KmsKeyId'] = snapshot.get('KmsKeyId', None)
            snapshot_dict['OwnerId'] = snapshot['OwnerId']
            snapshot_dict['Progress'] = snapshot['Progress']
            snapshot_dict['SnapshotId'] = snapshot['SnapshotId']
            snapshot_dict['StartTime'] = snapshot['StartTime']
            snapshot_dict['SnapshotAge'] = calculate_age(snapshot['StartTime'])
            snapshot_dict['State'] = snapshot['State']
            snapshot_dict['StateMessage'] = snapshot.get('StateMessage', None)
            snapshot_dict['VolumeId'] = snapshot['VolumeId']
            snapshot_dict['VolumeSize'] = snapshot['VolumeSize']
            snapshot_dict['OwnerAlias'] = snapshot.get('OwnerAlias', None)
            snapshot_dict['OutpostArn'] = snapshot.get('OutpostArn', None)
            snapshot_dict['Tags'] = snapshot_tags(snapshot.get('Tags',[]))
            snapshot_dict['StorageTier'] = snapshot['StorageTier']
            snapshot_dict['RestoreExpiryTime'] = snapshot.get('RestoreExpiryTime', None)
            snapshot_dict['SseType'] = snapshot.get('SseType', None)

            print(snapshot['SnapshotId'])

            snapshots_list.append(snapshot_dict)
            
# Create a DataFrame using pandas
df = pd.DataFrame(snapshots_list)

# Write the DataFrame to a CSV file
csv_filename = 'describe_snapshots.csv'
df.to_csv(csv_filename, index=False)
