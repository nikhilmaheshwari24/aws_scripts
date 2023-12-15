import boto3
import os
import sys
import pandas as pd

# Setting up the AWS Environment
env = str(sys.argv[1])  # Accepts the AWS profile name from the command line argument
os.environ['AWS_PROFILE'] = env  # Set the AWS profile using environment variables

regions = ['us-east-2']  # List of AWS regions to query

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
            # Dictionary to store Elasticache cluster details
            elasticache_dict = {
                'Region': region,
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
            }

            # Printing specific details for each Elasticache cluster
            print(cluster['CacheClusterId'], cluster['EngineVersion'])
        
            # Appending the Elasticache cluster details to the list
            elasticache_list.append(elasticache_dict)

# Creating a Pandas DataFrame from the list of Elasticache details
df = pd.DataFrame(elasticache_list)

# Exporting the DataFrame to a CSV file
filename = "ElastiCache.csv"
df.to_csv(filename)
