import boto3
import os
import sys
import pandas as pd

# Setting up the AWS Environment
# env = str(sys.argv[1])
# os.environ['AWS_PROFILE'] = env

regions = ['us-east-1', 'ap-southeast-1', 'ap-south-1']

session = boto3.Session()
profiles = session.available_profiles

elasticache_list = []

for profile in profiles:

    for region in regions:

        profile_session = boto3.session.Session(profile_name=profile)

        acc_info = profile_session.client('sts')
        acc_sts = acc_info.get_caller_identity()

        acc_no = acc_sts['Account']
        
        elasticache = profile_session.client('elasticache', region_name = region)
        paginator = elasticache.get_paginator('describe_cache_clusters')
        elasticache_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
        
        # print (elasticache_paginator)

        for page in elasticache_paginator:
            
            for cluster in page['CacheClusters']:

                elasticache_dict = {}
                elasticache_dict['Accounts'] = acc_no
                elasticache_dict['Region'] = region
                elasticache_dict['CacheClusterId'] = cluster['CacheClusterId']
                elasticache_dict['Engine'] = cluster['Engine']
                elasticache_dict['EngineVersion'] = cluster['EngineVersion']
                elasticache_dict['CacheClusterStatus'] = cluster['CacheClusterStatus']
                elasticache_dict['CacheNodeType'] = cluster['CacheNodeType']
                elasticache_dict['PreferredAvailabilityZone'] = cluster['PreferredAvailabilityZone']
                elasticache_dict['CacheClusterCreateTime'] = cluster['CacheClusterCreateTime']
                elasticache_dict['PreferredMaintenanceWindow'] = cluster['PreferredMaintenanceWindow']
                elasticache_dict['AutoMinorVersionUpgrade'] = cluster['AutoMinorVersionUpgrade']
                elasticache_dict['TransitEncryptionEnabled'] = cluster['TransitEncryptionEnabled']
                elasticache_dict['AtRestEncryptionEnabled'] = cluster['AtRestEncryptionEnabled']
                elasticache_dict['SnapshotRetentionLimit'] = cluster['SnapshotRetentionLimit']
                elasticache_dict['SnapshotWindow'] = cluster['SnapshotWindow']

                print (cluster['CacheClusterId'], cluster['EngineVersion'])
            
                elasticache_list.append(elasticache_dict)

df = pd.DataFrame(elasticache_list)
filename="ElastiCache.csv"
df.to_csv(filename)
            

            