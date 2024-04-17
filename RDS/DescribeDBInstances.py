# Import necessary libraries
import boto3
import os
import pandas as pd

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ""

# Define AWS regions to search for RDS instances
regions = ['us-east-1']

# Initialize an empty list to store RDS instance details
rds_info = []

# Iterate over each AWS region
for region in regions:

    # Create an RDS client for the specified region
    rds_client = boto3.client('rds', region_name=region)

    # Create a paginator for the describe_db_instances operation
    paginator = rds_client.get_paginator('describe_db_instances')

    # Paginate through the RDS instances
    rds_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})

    for page in rds_paginator:

        # Iterate through each RDS instance in the current page
        for db_instance in page['DBInstances']:

            # Initialize a dictionary to store details of the current RDS instance
            rds_details = {}

            # Assign values to dictionary keys
            rds_details['DBInstanceIdentifier'] = db_instance['DBInstanceIdentifier']
            rds_details['DBInstanceClass'] = db_instance['DBInstanceClass']
            rds_details['Engine'] = db_instance['Engine']
            rds_details['DBInstanceStatus'] = db_instance['DBInstanceStatus']
            rds_details['AutomaticRestartTime'] = db_instance.get('AutomaticRestartTime', None)
            rds_details['MasterUsername'] = db_instance.get('MasterUsername', None)
            rds_details['DBName'] = db_instance.get('DBName', None)
            rds_details['Endpoint_Address'] = db_instance['Endpoint']['Address']
            rds_details['Endpoint_Port'] = db_instance['Endpoint']['Port']
            rds_details['AllocatedStorage'] = db_instance['AllocatedStorage']
            rds_details['InstanceCreateTime'] = db_instance['InstanceCreateTime']
            rds_details['PreferredBackupWindow'] = db_instance['PreferredBackupWindow']
            rds_details['BackupRetentionPeriod'] = db_instance['BackupRetentionPeriod']
            rds_details['DBSecurityGroups'] = [group['DBSecurityGroupName'] for group in db_instance['DBSecurityGroups']]
            rds_details['VpcSecurityGroups'] = [group['VpcSecurityGroupId'] for group in db_instance['VpcSecurityGroups']]
            rds_details['DBParameterGroups'] = [group['DBParameterGroupName'] for group in db_instance['DBParameterGroups']]
            rds_details['AvailabilityZone'] = db_instance['AvailabilityZone']
            rds_details['DBSubnetGroup_DBSubnetGroupName'] = db_instance['DBSubnetGroup']['DBSubnetGroupName']
            rds_details['MultiAZ'] = db_instance['MultiAZ']
            rds_details['EngineVersion'] = db_instance['EngineVersion']
            rds_details['ReadReplicaSourceDBInstanceIdentifier'] = db_instance.get('ReadReplicaSourceDBInstanceIdentifier', None)
            rds_details['ReadReplicaDBInstanceIdentifiers'] = db_instance['ReadReplicaDBInstanceIdentifiers']
            rds_details['ReadReplicaDBClusterIdentifiers'] = db_instance.get('ReadReplicaDBClusterIdentifiers', None)
            rds_details['ReplicaMode'] = db_instance.get('ReplicaMode',None)
            rds_details['PubliclyAccessible'] = db_instance['PubliclyAccessible']
            rds_details['TdeCredentialArn'] = db_instance.get('TdeCredentialArn', None)
            rds_details['DbInstancePort'] = db_instance['DbInstancePort']
            rds_details['StorageEncrypted'] = db_instance['StorageEncrypted']
            rds_details['KmsKeyId'] = db_instance['KmsKeyId']
            rds_details['DbiResourceId'] = db_instance['DbiResourceId']
            rds_details['CACertificateIdentifier'] = db_instance['CACertificateIdentifier']
            rds_details['MonitoringInterval'] = db_instance['MonitoringInterval']
            rds_details['EnhancedMonitoringResourceArn'] = db_instance.get('EnhancedMonitoringResourceArn', None)
            rds_details['MonitoringRoleArn'] = db_instance.get('MonitoringRoleArn', None)
            rds_details['IAMDatabaseAuthenticationEnabled'] = db_instance['IAMDatabaseAuthenticationEnabled']
            rds_details['EnabledCloudwatchLogsExports'] = db_instance.get('EnabledCloudwatchLogsExports', None)
            rds_details['TagList'] = db_instance['TagList']
            rds_details['DeletionProtection'] = db_instance['DeletionProtection']
            rds_details['MaxAllocatedStorage'] = db_instance.get('MaxAllocatedStorage', None)
            rds_details['AssociatedRoles'] = db_instance['AssociatedRoles']
            rds_details['PreferredMaintenanceWindow'] = db_instance['PreferredMaintenanceWindow']
            rds_details['AutoMinorVersionUpgrade'] = db_instance['AutoMinorVersionUpgrade']
            rds_details['StorageType'] = db_instance['StorageType']
            rds_details['Iops'] = db_instance.get('Iops', None)
            rds_details['StorageThroughput'] = db_instance.get('StorageThroughput', None)
            rds_details['CopyTagsToSnapshot'] = db_instance['CopyTagsToSnapshot']
            rds_details['PerformanceInsightsEnabled'] = db_instance.get('PerformanceInsightsEnabled', None)
            rds_details['PerformanceInsightsKMSKeyId'] = db_instance.get('PerformanceInsightsKMSKeyId', None)
            rds_details['PerformanceInsightsRetentionPeriod'] = db_instance.get('PerformanceInsightsRetentionPeriod', None)
            rds_details['DeletionProtection'] = db_instance['DeletionProtection']
            rds_details['DBClusterIdentifier'] = db_instance.get('DBClusterIdentifier', None)
            rds_details['DBSubnetGroupName'] = db_instance['DBSubnetGroup']['DBSubnetGroupName']
            rds_details['DBSubnetGroupDescription'] = db_instance['DBSubnetGroup']['DBSubnetGroupDescription']
            rds_details['VpcId'] = db_instance['DBSubnetGroup']['VpcId']
            rds_details['SubnetGroupStatus'] = db_instance['DBSubnetGroup']['SubnetGroupStatus']
            rds_details['DBInstanceAutomatedBackupsReplications'] = db_instance.get('DBInstanceAutomatedBackupsReplications', None)
            rds_details['CertificateDetails'] = db_instance['CertificateDetails']
            rds_details['ReadReplicaSourceDBClusterIdentifier'] = db_instance.get('ReadReplicaSourceDBClusterIdentifier', None)

            if 'MasterUserSecret' in db_instance:
                rds_details['MasterUserSecret'] = {
                    'SecretArn': db_instance['MasterUserSecret'].get('SecretArn', None),
                    'SecretStatus': db_instance['MasterUserSecret'].get('SecretStatus', None),
                    'KmsKeyId': db_instance['MasterUserSecret'].get('KmsKeyId', None)
                }
            else:
                rds_details['MasterUserSecret'] = {
                    'SecretArn': None,
                    'SecretStatus': None,
                    'KmsKeyId': None
                }

            rds_details['CertificateDetails'] = {
                'CAIdentifier': db_instance['CertificateDetails']['CAIdentifier'],
                'ValidTill': db_instance['CertificateDetails']['ValidTill']
            }
            rds_details['ReadReplicaSourceDBClusterIdentifier'] = db_instance.get('ReadReplicaSourceDBClusterIdentifier', None)
            rds_details['PercentProgress'] = db_instance.get('PercentProgress', None)
            rds_details['DedicatedLogVolume'] = db_instance.get('DedicatedLogVolume', None)
            rds_details['IsStorageConfigUpgradeAvailable'] = db_instance.get('IsStorageConfigUpgradeAvailable', None)
            rds_details['MultiTenant'] = db_instance.get('MultiTenant', None)
            rds_details['CustomerOwnedIpEnabled'] = db_instance['CustomerOwnedIpEnabled']
            rds_details['AwsBackupRecoveryPointArn'] = db_instance.get('AwsBackupRecoveryPointArn', None)
            rds_details['ActivityStreamStatus'] = db_instance['ActivityStreamStatus']
            rds_details['ActivityStreamKmsKeyId'] = db_instance.get('ActivityStreamKmsKeyId', None)
            rds_details['ActivityStreamKinesisStreamName'] = db_instance.get('ActivityStreamKinesisStreamName', None)
            rds_details['ActivityStreamMode'] = db_instance.get('ActivityStreamMode', None)
            rds_details['ActivityStreamEngineNativeAuditFieldsIncluded'] = db_instance.get('ActivityStreamEngineNativeAuditFieldsIncluded', None)
            rds_details['AutomationMode'] = db_instance.get('AutomationMode', None)
            rds_details['ResumeFullAutomationModeTime'] = db_instance.get('ResumeFullAutomationModeTime', None)
            rds_details['CustomIamInstanceProfile'] = db_instance.get('CustomIamInstanceProfile', None)
            rds_details['BackupTarget'] = db_instance.get('BackupTarget', None)
            rds_details['NetworkType'] = db_instance.get('NetworkType', None)
            rds_details['ActivityStreamPolicyStatus'] = db_instance.get('ActivityStreamPolicyStatus', None)
            rds_details['StorageThroughput'] = db_instance.get('StorageThroughput', None)
            rds_details['DBSystemId'] = db_instance.get('DBSystemId', None)

            # Append the details of the current RDS instance to the list
            rds_info.append(rds_details)

# Create a DataFrame using pandas
df = pd.DataFrame(rds_info)

# Write the DataFrame to a CSV file
csv_filename = 'rds_describe.csv'
df.to_csv(csv_filename, index=False)
