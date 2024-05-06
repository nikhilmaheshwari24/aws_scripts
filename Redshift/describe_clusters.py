import boto3
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define AWS regions to search for Redshift clusters
regions = ['ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

# Initialize a list to store Redshift cluster information
clusters_list = []

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
    tag_list = []
    for tag in resource_tags_list:
        key = tag['Key']
        value = tag['Value']
        tag_list.append(f"{key}: {value}")
    if tag_list:
        return '\n'.join(tag_list)
    else:
        return "No Tags Available"

# Function to extract the resource name from tags
def get_resource_name(resource_tags_list):
    if resource_tags_list:
        for tag in resource_tags_list:
            if 'Name' == tag['Key']:
                return tag['Value']
    else:
        return None

# Iterate over each region
for region in regions:
    # Create a Redshift client for the region
    redshift_client = boto3.client('redshift', region_name=region)
    # Paginate through the list of Redshift clusters
    paginator = redshift_client.get_paginator('describe_clusters')
    clusters_paginator = paginator.paginate(PaginationConfig={'MaxItems': 100})

    # Iterate over each page of Redshift clusters
    for page in clusters_paginator:
        # Iterate over each Redshift cluster
        for cluster in page['Clusters']:

            # Initialize a dictionary to store cluster information
            cluster_dict = {}
        
            # Extract Redshift cluster details
            cluster_dict['Region'] = region
            cluster_dict['ClusterName'] = get_resource_name(cluster.get('Tags', []))
            cluster_dict['ClusterIdentifier'] = cluster['ClusterIdentifier']
            cluster_dict['NodeType'] = cluster['NodeType']
            cluster_dict['ClusterStatus'] = cluster['ClusterStatus']
            cluster_dict['ClusterAvailabilityStatus'] = cluster['ClusterAvailabilityStatus']
            cluster_dict['ModifyStatus'] = cluster.get('ModifyStatus', None)
            cluster_dict['MasterUsername'] = cluster['MasterUsername']
            cluster_dict['DBName'] = cluster['DBName']
            cluster_dict['Endpoint'] = cluster['Endpoint']
            cluster_dict['ClusterCreateTime'] = cluster['ClusterCreateTime']
            cluster_dict['ClusterAge'] = calculate_age(cluster['ClusterCreateTime'])
            cluster_dict['AutomatedSnapshotRetentionPeriod'] = cluster['AutomatedSnapshotRetentionPeriod']
            cluster_dict['ManualSnapshotRetentionPeriod'] = cluster['ManualSnapshotRetentionPeriod']
            cluster_dict['ClusterSecurityGroups'] = cluster['ClusterSecurityGroups']
            cluster_dict['VpcSecurityGroups'] = cluster['VpcSecurityGroups']
            cluster_dict['ClusterParameterGroups'] = cluster['ClusterParameterGroups']
            cluster_dict['ClusterSubnetGroupName'] = cluster['ClusterSubnetGroupName']
            cluster_dict['VpcId'] = cluster['VpcId']
            cluster_dict['AvailabilityZone'] = cluster['AvailabilityZone']
            cluster_dict['PreferredMaintenanceWindow'] = cluster['PreferredMaintenanceWindow']
            cluster_dict['PendingModifiedValues'] = cluster['PendingModifiedValues']
            cluster_dict['ClusterVersion'] = cluster['ClusterVersion']
            cluster_dict['AllowVersionUpgrade'] = cluster['AllowVersionUpgrade']
            cluster_dict['NumberOfNodes'] = cluster['NumberOfNodes']
            cluster_dict['PubliclyAccessible'] = cluster['PubliclyAccessible']
            cluster_dict['Encrypted'] = cluster['Encrypted']
            cluster_dict['RestoreStatus'] = cluster.get('RestoreStatus', {})
            cluster_dict['DataTransferProgress'] = cluster.get('DataTransferProgress',{})
            cluster_dict['HsmStatus'] = cluster.get('HsmStatus', {})
            cluster_dict['ClusterSnapshotCopyStatus'] = cluster.get('HsmStatus', {})
            cluster_dict['ClusterPublicKey'] = cluster['ClusterPublicKey']
            cluster_dict['ClusterNodes'] = cluster['ClusterNodes']
            cluster_dict['ElasticIpStatus'] = cluster.get('ElasticIpStatus', {})
            cluster_dict['ClusterRevisionNumber'] = cluster['ClusterRevisionNumber']
            cluster_dict['Tags'] = resource_tags(cluster.get('Tags', []))
            cluster_dict['KmsKeyId'] = cluster['KmsKeyId']
            cluster_dict['EnhancedVpcRouting'] = cluster['EnhancedVpcRouting']
            cluster_dict['IamRoles'] = cluster['IamRoles']
            cluster_dict['PendingActions'] = cluster.get('PendingActions', [])
            cluster_dict['MaintenanceTrackName'] = cluster['MaintenanceTrackName']
            cluster_dict['ElasticResizeNumberOfNodeOptions'] = cluster.get('ElasticResizeNumberOfNodeOptions', None)
            cluster_dict['DeferredMaintenanceWindows'] = cluster['DeferredMaintenanceWindows']
            cluster_dict['SnapshotScheduleIdentifier'] = cluster.get('SnapshotScheduleIdentifier', None)
            cluster_dict['SnapshotScheduleState'] = cluster.get('SnapshotScheduleState', None)
            cluster_dict['ExpectedNextSnapshotScheduleTime'] = cluster.get('ExpectedNextSnapshotScheduleTime', None)
            cluster_dict['ExpectedNextSnapshotScheduleTimeStatus'] = cluster.get('ExpectedNextSnapshotScheduleTimeStatus', None)
            cluster_dict['NextMaintenanceWindowStartTime'] = cluster['NextMaintenanceWindowStartTime']
            cluster_dict['ResizeInfo'] = cluster.get('ResizeInfo', {})
            cluster_dict['AvailabilityZoneRelocationStatus'] = cluster['AvailabilityZoneRelocationStatus']
            cluster_dict['ClusterNamespaceArn'] = cluster['ClusterNamespaceArn']
            cluster_dict['TotalStorageCapacityInMegaBytes'] = cluster['TotalStorageCapacityInMegaBytes']
            cluster_dict['AquaConfiguration'] = cluster['AquaConfiguration']
            cluster_dict['DefaultIamRoleArn'] = cluster.get('DefaultIamRoleArn', None)
            cluster_dict['ReservedNodeExchangeStatus'] = cluster.get('ReservedNodeExchangeStatus', {})
            cluster_dict['CustomDomainName'] = cluster.get('CustomDomainName', None)
            cluster_dict['CustomDomainCertificateArn'] = cluster.get('CustomDomainCertificateArn', None)
            cluster_dict['CustomDomainCertificateExpiryDate'] = cluster.get('CustomDomainCertificateArn', None)
            cluster_dict['MasterPasswordSecretArn'] = cluster.get('MasterPasswordSecretArn', None)
            cluster_dict['MasterPasswordSecretKmsKeyId'] = cluster.get('MasterPasswordSecretKmsKeyId', None)
            cluster_dict['IpAddressType'] = cluster.get('IpAddressType')
            cluster_dict['MultiAZ'] = cluster['MultiAZ']
            cluster_dict['MultiAZSecondary'] = cluster.get('MultiAZSecondary', {})

            # Append Redshift cluster details to the list
            clusters_list.append(cluster_dict)

            # Print Redshift cluster information
            print(cluster_dict['Region'], " <> ", cluster_dict['DBName'], " <> ", cluster_dict['ClusterAge'])

# Create DataFrame
df = pd.DataFrame(clusters_list)

# Write DataFrame to CSV file
filename = 'describe_clusters.csv'
df.to_csv(os.path.join(directory, filename), index=False)
