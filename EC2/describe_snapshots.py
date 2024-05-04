import boto3
import os
import pandas as pd
from datetime import datetime, timezone

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define AWS regions to search for EBS Volumes
regions = ['us-east-2']

snapshots_list = []

# Define a directory to store CSV files
directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

# Function to calculate age based on creation date
def calculate_age(create_date):
    create_date = datetime.fromisoformat(str(create_date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

# Function to extract resource tags
def resource_tags(resource_tags_list):
    # Initialize an empty list to store tags
    tag_list = []
    # Process each tag and store it in the list
    for tag in resource_tags_list:
        key = tag['Key']
        value = tag['Value']
        tag_list.append(f"{key}: {value}")
    # Return the concatenated tags if tags are present
    if tag_list:
        return '\n'.join(tag_list)
    else:
        return "No Tags Available"

# Function to fetch volume type
def fetch_volume_type(volume_id, ec2_client):

    try:
        response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        volume_type = response['Volumes'][0]['VolumeType']
        return volume_type
    except boto3.exceptions.botocore.client.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidVolume.NotFound':
            return "Volume Doesn't Exist"
        else:
            return f"Error: {error_code}"

# Iterate over each region
for region in regions:
    # Create an EC2 client for the region
    ec2_client = boto3.client('ec2',region_name=region)
    # Describe snapshots
    paginator = ec2_client.get_paginator('describe_snapshots')
    ec2_paginator = paginator.paginate(PaginationConfig={'PageSize': 100},OwnerIds=['self'])
    # Iterate over each page of snapshots
    for page in ec2_paginator:
        # Iterate over each snapshot
        for snapshot in page['Snapshots']:
            snapshot_dict = {}
            # Extract snapshot details
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
            snapshot_dict['VolumeType'] = fetch_volume_type(snapshot['VolumeId'], ec2_client)
            snapshot_dict['OwnerAlias'] = snapshot.get('OwnerAlias', None)
            snapshot_dict['OutpostArn'] = snapshot.get('OutpostArn', None)
            snapshot_dict['Tags'] = resource_tags(snapshot.get('Tags',[]))
            snapshot_dict['StorageTier'] = snapshot['StorageTier']
            snapshot_dict['RestoreExpiryTime'] = snapshot.get('RestoreExpiryTime', None)
            snapshot_dict['SseType'] = snapshot.get('SseType', None)
            # Print Snapshot Id
            print(snapshot['SnapshotId'])
            snapshots_list.append(snapshot_dict)

# Create a DataFrame using pandas
df = pd.DataFrame(snapshots_list)

# Write the DataFrame to a CSV file
filename = 'describe_snapshots.csv'
df.to_csv(os.path.join(directory, filename), index=False)
