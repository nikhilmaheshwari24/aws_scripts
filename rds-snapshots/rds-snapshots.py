import boto3
import os
import sys
import csv
from datetime import datetime, timezone
import pandas as pd

# AWS Profiling
env=str(sys.argv[1])
os.environ['AWS_PROFILE'] = env

manual_snapshots = []

regions = ['us-east-2', 'us-east-1', 'us-west-1', 'us-west-2', 'ap-south-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ca-central-1', 'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'sa-east-1']

for region in regions:
    rds = boto3.client('rds', region_name = region)


    #Get rds manual snapshots for all db instances
    paginator = rds.get_paginator('describe_db_snapshots')
    response_iterator = paginator.paginate(SnapshotType="manual")


    for page in response_iterator:
        for snapshot in page['DBSnapshots']:
            dict = {}

            dict['Manual Snapshot'] = snapshot['DBSnapshotIdentifier']
            dict['Age of Manual Snapshot'] = (datetime.now(timezone.utc) - snapshot['SnapshotCreateTime']).days
            dict['Manual Snapshot Creation Time'] = snapshot['SnapshotCreateTime']
            dict['Region'] = region

            try:
                response = rds.describe_db_instance_automated_backups(DBInstanceIdentifier=snapshot['DBInstanceIdentifier'])
                dict['Instance Name'] = snapshot['DBInstanceIdentifier']
                dict['Status'] = "Present"
                dict['Automated Snapshot'] = "Enabled"
                dict['Latest Automated Snapshot Taken'] = response['DBInstanceAutomatedBackups'][0]['RestoreWindow']['LatestTime']
                dict['Automated Backup Retention'] = response['DBInstanceAutomatedBackups'][0]['BackupRetentionPeriod']
            except:
                dict['Instance Name'] = snapshot['DBInstanceIdentifier'] 
                dict['Status'] = "Absent"
                dict['Automated Snapshot'] = "-"
                dict['Latest Automated Snapshot Taken'] = "-"
                dict['Automated Backup Retention'] = "-"

            manual_snapshots.append(dict)

    #Get rds manual snapshots for aurora DB instances
    paginator = rds.get_paginator('describe_db_cluster_snapshots')
    response_iterator = paginator.paginate(SnapshotType="manual")

    for page in response_iterator:
        for snapshot in page['DBClusterSnapshots']:
            dict = {}

            dict['Manual Snapshot'] = snapshot['DBClusterSnapshotIdentifier']
            dict['Age of Manual Snapshot'] = (datetime.now(timezone.utc) - snapshot['SnapshotCreateTime']).days
            dict['Manual Snapshot Creation Time'] = snapshot['SnapshotCreateTime']
            dict['Region'] = region

            try:
                response = rds.describe_db_clusters(DBClusterIdentifier=snapshot['DBClusterIdentifier'])
                dict['Instance Name'] = snapshot['DBClusterIdentifier']
                dict['Status'] = "Present"
                dict['Automated Snapshot'] = "Enabled"
                dict['Latest Automated Snapshot Taken'] = response['DBClusters'][0]['LatestRestorableTime']
                dict['Automated Backup Retention'] = response['DBClusters'][0]['BackupRetentionPeriod']
            except Exception as e:
                dict['Instance Name'] = snapshot['DBClusterIdentifier'] 
                dict['Status'] = "Absent"
                dict['Automated Snapshot'] = "-"
                dict['Latest Automated Snapshot Taken'] = "-"
                dict['Automated Backup Retention'] = "-"

            manual_snapshots.append(dict)
        

df = pd.DataFrame(manual_snapshots)
# print(df)
filename="Delhivery-" + env + ".csv"
df.to_csv(filename)