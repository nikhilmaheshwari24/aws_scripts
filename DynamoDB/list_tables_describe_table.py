import boto3
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

os.environ['AWS_PROFILE'] = '683738265913_admin_exp_permission_set'

regions = ['ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']

tabless_list = []

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

# Function to extract resource name from tags
def get_resource_name(resource_tags_list):
    if resource_tags_list:
        for tag in resource_tags_list:
            if 'Name' == tag['Key']:
                return tag['Value']
    else:
        return None

for region in regions:

    ddb_client = boto3.client('dynamodb', region_name = region)
    paginator = ddb_client.get_paginator('list_tables')
    tables_paginator = paginator.paginate(PaginationConfig={'MaxItems': 100})

    for page in tables_paginator:

        for table in page['TableNames']:

            table_dict = {}
        
            table_dict['Region'] = region
            # cluster_dict['ClusterName'] = get_resource_name(table.get('Tags', []))
            table_dict['TableName'] = table

            table_info = ddb_client.describe_table(TableName=table)['Table']
            # table_dict[''] = table_info['']

            # print(table_info)
            
            table_dict['AttributeDefinitions'] = table_info['AttributeDefinitions']
            table_dict['KeySchema'] = table_info['KeySchema']
            table_dict['TableStatus'] = table_info['TableStatus']
            table_dict['CreationDateTime'] = table_info['CreationDateTime']
            table_dict['Age'] = calculate_age(table_info['CreationDateTime'])
            table_dict['ProvisionedThroughput'] = table_info['ProvisionedThroughput']
            table_dict['TableSizeBytes'] = table_info['TableSizeBytes']
            table_dict['ItemCount'] = table_info['ItemCount']
            table_dict['TableArn'] = table_info['TableArn']
            table_dict['TableId'] = table_info['TableId']
            table_dict['BillingModeSummary'] = table_info.get('BillingModeSummary', {})
            table_dict['LocalSecondaryIndexes'] = table_info.get('LocalSecondaryIndexes', [])
            table_dict['GlobalSecondaryIndexes'] = table_info.get('GlobalSecondaryIndexes', [])
            table_dict['StreamSpecification'] = table_info.get('StreamSpecification', {})
            table_dict['LatestStreamLabel'] = table_info.get('LatestStreamLabel', None)
            table_dict['LatestStreamArn'] = table_info.get('LatestStreamArn', None)
            table_dict['GlobalTableVersion'] = table_info.get('GlobalTableVersion', None)
            table_dict['Replicas'] = table_info.get('Replicas', [])
            table_dict['RestoreSummary'] = table_info.get('RestoreSummary')
            table_dict['SSEDescription'] = table_info.get('SSEDescription', {})
            table_dict['ArchivalSummary'] = table_info.get('ArchivalSummary', {})
            table_dict['TableClassSummary'] = table_info.get('TableClassSummary', {})
            table_dict['DeletionProtectionEnabled'] = table_info['DeletionProtectionEnabled']
            table_dict['OnDemandThroughput'] = table_info.get('OnDemandThroughput', {})

            tabless_list.append(table_dict)

            print(table_dict['Region'], " <> ", table_dict['TableName'], " <> ")

# Create DataFrame
df = pd.DataFrame(tabless_list)

# Write DataFrame to CSV file
filename = 'list_tables.csv'
df.to_csv(os.path.join(directory, filename), index=False)
