import boto3
import os
import sys
import math
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Command python3.11 elasticacheDescribeSingleAccount.py <profile_name>

# Setting up the AWS Environment
env = str(sys.argv[1])  # Accepts the AWS profile name from the command line argument
os.environ['AWS_PROFILE'] = env  # Set the AWS profile using environment variables

regions = ['us-east-2']  # List of AWS regions to query

# Function to retrieve CPU metric data for Elasticache cluster
def get_elasticache_cpu_metric(redis_node, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Define time range (1 week ago to current time)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(weeks=1)

    # Get CPUUtilization metric data
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/ElastiCache',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'CacheClusterId', 'Value': redis_node}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Maximum'],  # Fetch maximum value
        Unit='Percent'
    )

    return response

# Calculate p99 from the maximum values
def calculate_p99(metric_data):
    datapoints = metric_data['Datapoints']
    if datapoints:
        values = [point['Maximum'] for point in datapoints]
        p99 = np.percentile(values, 99)
        return p99
    return None

elasticache_list = []  # Initialize an empty list to store Elasticache details

for region in regions:
    # Creating an Elasticache client for the specific region
    elasticache = boto3.client('elasticache', region_name=region)
    
    # Paginator for describe_cache_clusters API call with a page size of 50
    paginator = elasticache.get_paginator('describe_cache_clusters')
    elasticache_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
    
    # Iterate through the paginated results
    for page in elasticache_paginator:
        for cluster in page['CacheClusters']:

            # Retrieve and calculate CPUUtilization (P99) for the cluster
            cpuUtilisation = get_elasticache_cpu_metric(cluster['CacheClusterId'], region)
            p99_cpu = calculate_p99(cpuUtilisation)
            
            # Dictionary to store Elasticache cluster details
            elasticache_dict = {
                'Region': region,
                'ReplicationGroupId': cluster['ReplicationGroupId'],
                'CacheClusterId': cluster['CacheClusterId'],
                'Engine': cluster['Engine'],
                'EngineVersion': cluster['EngineVersion'],
                'CacheClusterStatus': cluster['CacheClusterStatus'],
                'CacheNodeType': cluster['CacheNodeType'],
                'PreferredAvailabilityZone': cluster['PreferredAvailabilityZone'],
                'CacheClusterCreateTime': cluster['CacheClusterCreateTime'],
                'PreferredMaintenanceWindow': cluster['PreferredMaintenanceWindow'],
                'AutoMinorVersionUpgrade': cluster['AutoMinorVersionUpgrade'],
                'TransitEncryptionEnabled': cluster['TransitEncryptionEnabled'],
                'AtRestEncryptionEnabled': cluster['AtRestEncryptionEnabled'],
                'SnapshotRetentionLimit': cluster['SnapshotRetentionLimit'],
                'SnapshotWindow': cluster['SnapshotWindow']
                'CPUUtilisation (P99)': str(math.floor(p99_cpu)) + "%"
            }

            # Printing specific details for each Elasticache cluster
            print(cluster['CacheClusterId'], cluster['EngineVersion'], str(math.floor(p99_cpu)) + "%")
        
            # Appending the Elasticache cluster details to the list
            elasticache_list.append(elasticache_dict)

# Creating a Pandas DataFrame from the list of Elasticache details
df = pd.DataFrame(elasticache_list)

# Exporting the DataFrame to a CSV file
filename = "ElastiCache_ + "env" +.csv"
df.to_csv(filename)
