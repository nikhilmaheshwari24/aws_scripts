import boto3
import os
import sys
import csv
from datetime import datetime, timezone
import pandas as pd

# AWS Profiling
env=str(sys.argv[1])
os.environ['AWS_PROFILE'] = env

regions = ['ap-south-1', 'ap-southeast-1', 'us-east-1']

manual_snapshots = []

for region in regions:

    elasticache = boto3.client('elasticache', region_name=region)
    paginator = elasticache.get_paginator('describe_snapshots')
    elasticache_paginator = paginator.paginate(SnapshotSource="user", PaginationConfig={'PageSize': 50})
    cache_clusters = elasticache.describe_cache_clusters()['CacheClusters']

    for page in elasticache_paginator:
        for snapshot in page['Snapshots']:
            dict = {}

            print (snapshot['SnapshotName'])

            dict['Manual Snapshot'] = snapshot['SnapshotName']
            dict['Age of Manual Snapshot'] = (datetime.now(timezone.utc) - snapshot['NodeSnapshots'][0]['SnapshotCreateTime']).days
            dict['Manual Snapshot Creation Time'] = snapshot['NodeSnapshots'][0]['SnapshotCreateTime']
            dict['Region'] = region
            # dict['Snapshot Status'] = snapshot['SnapshotStatus']
            
            try:
                dict['Cluster/Node']=snapshot['ReplicationGroupId']
                # dict['Snapshot Type']="Cluster Snapshot"
                try:
                    if snapshot['ReplicationGroupId'] is not None:
                        redis=elasticache.describe_replication_groups(ReplicationGroupId=snapshot['ReplicationGroupId'])
                        dict['Cluster Status']=redis['ReplicationGroups'][0]['Status']
                        dict['Automatic Backup']="Enabled"
                        dict['Automatic Backup Window']=snapshot['SnapshotWindow']
                        dict['Automatic Backup Retention']=snapshot['SnapshotRetentionLimit']
                except:
                    dict['Cluster Status']="-"
                    dict['Automatic Backup']="-"
                    dict['Automatic Backup Window']="-"
                    dict['Automatic Backup Retention']="-"
            except:
                dict['Cluster/Node']=snapshot['CacheClusterId']
                # dict['Snapshot Type']="Cluster Node Snapshot"
                try:
                    if snapshot['CacheClusterId'] is not None:
                        redis=elasticache.describe_cache_clusters(CacheClusterId=snapshot['CacheClusterId'])
                        dict['Cluster Status']=redis['CacheClusters'][0]['CacheClusterStatus']
                        dict['Automatic Backup']="Enabled"
                        dict['Automatic Backup Window']=snapshot['SnapshotWindow']
                        dict['Automatic Backup Retention']=snapshot['SnapshotRetentionLimit']
                except:
                    dict['Cluster Status']="-"
                    dict['Automatic Backup']="-"
                    dict['Automatic Backup Window']="-"
                    dict['Automatic Backup Retention']="-"

            dict["Can we delete these Manual Snapshots?"]=""
           
            manual_snapshots.append(dict)

df = pd.DataFrame(manual_snapshots)
# print(df)
filename="Delhivery-" + env + ".csv"
df.to_csv(filename)