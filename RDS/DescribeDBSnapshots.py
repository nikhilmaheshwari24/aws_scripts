# Import necessary libraries
import boto3
import os
import pandas as pd
from datetime import datetime, timezone

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = "683738265913_admin_exp_permission_set"

# Define AWS regions to search for RDS snapshots
regions = ['us-east-2']

# Initialize an empty list to store RDS snapshot details
snapshot_info = []

# Iterate over each AWS region
for region in regions:

    # Create an RDS client for the specified region
    rds_client = boto3.client('rds', region_name=region)
    
    # Create a paginator for describing DB snapshots
    paginator = rds_client.get_paginator('describe_db_snapshots')
    rds_paginator = paginator.paginate(IncludeShared=True,IncludePublic=True,PaginationConfig={'PageSize': 100})

    # Iterate through each page of DB snapshots
    for page in rds_paginator:

        # Iterate through each snapshot in the page
        for snapshot in page['DBSnapshots']:

            # Initialize a dictionary to store details of the current snapshot
            snapshot_details = {}

            # Assign values to dictionary keys
            snapshot_details['DBSnapshotIdentifier'] = snapshot['DBSnapshotIdentifier']
            snapshot_details['DBInstanceIdentifier'] = snapshot['DBInstanceIdentifier']
            snapshot_details['SnapshotCreateTime'] = snapshot['SnapshotCreateTime']
            snapshot_details['AgeOfSnapshot'] = (datetime.now(timezone.utc) - snapshot['SnapshotCreateTime']).days
            snapshot_details['Engine'] = snapshot['Engine']
            snapshot_details['AllocatedStorage'] = snapshot['AllocatedStorage']
            snapshot_details['Status'] = snapshot['Status']
            snapshot_details['Port'] = snapshot['Port']
            snapshot_details['AvailabilityZone'] = snapshot.get('AvailabilityZone',None)
            snapshot_details['VpcId'] = snapshot.get('VpcId', None)
            snapshot_details['InstanceCreateTime'] = snapshot['InstanceCreateTime']
            snapshot_details['MasterUsername'] = snapshot['MasterUsername']
            snapshot_details['EngineVersion'] = snapshot['EngineVersion']
            snapshot_details['LicenseModel'] = snapshot['LicenseModel']
            snapshot_details['SnapshotType'] = snapshot['SnapshotType']
            snapshot_details['Iops'] = snapshot.get('Iops', None)
            snapshot_details['OptionGroupName'] = snapshot.get('OptionGroupName', None)
            snapshot_details['PercentProgress'] = snapshot.get('PercentProgress', None)
            snapshot_details['SourceRegion'] = snapshot.get('SourceRegion', None)
            snapshot_details['SourceDBSnapshotIdentifier'] = snapshot.get('SourceDBSnapshotIdentifier', None)
            snapshot_details['StorageType'] = snapshot['StorageType']
            snapshot_details['TdeCredentialArn'] = snapshot.get('TdeCredentialArn', None)
            snapshot_details['Encrypted'] = snapshot['Encrypted']
            snapshot_details['KmsKeyId'] = snapshot.get('KmsKeyId', None)
            snapshot_details['DBSnapshotArn'] = snapshot['DBSnapshotArn']
            snapshot_details['Timezone'] = snapshot.get('Timezone', None)
            snapshot_details['IAMDatabaseAuthenticationEnabled'] = snapshot['IAMDatabaseAuthenticationEnabled']
            snapshot_details['ProcessorFeatures'] = snapshot['ProcessorFeatures']
            snapshot_details['DbiResourceId'] = snapshot.get('DbiResourceId', None)
            snapshot_details['TagList'] = snapshot.get('TagList', None)
            snapshot_details['OriginalSnapshotCreateTime'] = snapshot.get('OriginalSnapshotCreateTime', None)
            snapshot_details['SnapshotDatabaseTime'] = snapshot.get('SnapshotDatabaseTime', None)
            snapshot_details['SnapshotTarget'] = snapshot['SnapshotTarget']
            snapshot_details['StorageThroughput'] = snapshot.get('StorageThroughput', None)
            snapshot_details['DBSystemId'] = snapshot.get('DBSystemId', None)
            snapshot_details['DedicatedLogVolume'] = snapshot.get('DedicatedLogVolume', None)
            snapshot_details['MultiTenant'] = snapshot.get('MultiTenant', None)

            # Append the details of the current snapshot to the list
            snapshot_info.append(snapshot_details)

# Create a DataFrame using pandas
df = pd.DataFrame(snapshot_info)

# Write the DataFrame to a CSV file
csv_filename = 'rds_snapshots_describe.csv'
df.to_csv(csv_filename, index=False)
