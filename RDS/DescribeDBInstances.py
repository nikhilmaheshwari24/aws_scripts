import boto3
import os
import pandas as pd

# Set AWS profile
os.environ['AWS_PROFILE'] = '683738265913_admin_exp_permission_set'

# Enter the region
regions=['us-east-2']

# List to store RDS instance details
rds_info = []

# Iterate over each region
for region in regions:
    # Create an RDS client
    rds_client = boto3.client('rds', region_name=region)
    
    # Create a paginator for describe_db_instances API
    paginator = rds_client.get_paginator('describe_db_instances')
    
    # Paginate through the results
    rds_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

    # Iterate over each page of RDS instances
    for page in rds_paginator:
        # Iterate over each RDS instance
        for instance in page['DBInstances']:
            # Dictionary to store instance details
            instance_details = {}

            # Populate instance details
            instance_details['DBInstanceIdentifier'] = instance['DBInstanceIdentifier']
            instance_details['DBInstanceClass'] = instance['DBInstanceClass']
            instance_details['Engine'] = instance['Engine']
            instance_details['EngineVersion'] = instance['EngineVersion']
            instance_details['DBInstanceStatus'] = instance['DBInstanceStatus']
            instance_details['Endpoint_Address'] = instance['Endpoint']['Address']
            instance_details['Endpoint_Port'] = instance['Endpoint']['Port']
            instance_details['AllocatedStorage'] = instance['AllocatedStorage']
            instance_details['MultiAZ'] = instance['MultiAZ']
            instance_details['BackupRetentionPeriod'] = instance['BackupRetentionPeriod']
            instance_details['PreferredMaintenanceWindow'] = instance['PreferredMaintenanceWindow']
            instance_details['AutoMinorVersionUpgrade'] = instance['AutoMinorVersionUpgrade']
            instance_details['PubliclyAccessible'] = instance['PubliclyAccessible']
            instance_details['StorageType'] = instance['StorageType']
            instance_details['Iops'] = instance['Iops']
            instance_details['StorageThroughput'] = instance['StorageThroughput']
            instance_details['CopyTagsToSnapshot'] = instance['CopyTagsToSnapshot']

            # Add PerformanceInsightsRetentionPeriod only if PerformanceInsightsEnabled is True
            if instance['PerformanceInsightsEnabled']:
                instance_details['PerformanceInsightsRetentionPeriod'] = instance['PerformanceInsightsRetentionPeriod']
          
            instance_details['PerformanceInsightsEnabled'] = instance['PerformanceInsightsEnabled']
            instance_details['DeletionProtection'] = instance['DeletionProtection']
            instance_details['TagList'] = instance['TagList']

            # Append instance details to the list
            rds_info.append(instance_details)
            print(instance['DBInstanceIdentifier'])

# Create a DataFrame from the list of instance details
dataframe = pd.DataFrame(rds_info)

# Save DataFrame to a CSV file
filename = "RDS_Instances.csv"
dataframe.to_csv(filename, index=False)
