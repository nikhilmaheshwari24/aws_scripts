import boto3
import os
import pandas as pd
from datetime import datetime

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define AWS regions to search for CloudWatch Logs
regions = ['us-east-2']

# Initialize a list to store CloudWatch log group information
logs_list = []

# Define a directory to store CSV files
directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

# Function for converting bytes to a human-readable format
def human_readable_bytes(value):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    while value >= 1000 and unit_index < len(units) - 1:
        value /= 1000
        unit_index += 1
    return f"{value:.2f}{units[unit_index]}"

# Function for converting epoch time to human-readable format
def convert_epoch_to_human_readable(epoch_time):
    try:
        dt_object = datetime.utcfromtimestamp(epoch_time)
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        return f"Error: {e}"

# Function to calculate age based on creation date
def calculate_age(create_date):
    create_date = datetime.fromisoformat(str(create_date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

# Iterate over each region
for region in regions:
    # Create a CloudWatch Logs client for the region
    log_client = boto3.client('logs', region_name=region)
    # Describe log groups
    paginator = log_client.get_paginator('describe_log_groups')
    logs_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
    # Iterate over each page of log groups
    for page in logs_paginator:
        # Iterate over each log group
        for logGroup in page['logGroups']:
            log_dict = {}
            # Extract log group details
            log_dict['logGroupName'] = logGroup['logGroupName']
            log_dict['creationTime'] = convert_epoch_to_human_readable(logGroup['creationTime'])
            log_dict['creationTime'] = calculate_age(logGroup['creationTime'])
            log_dict['retentionInDays'] = logGroup.get('retentionInDays', None)
            log_dict['metricFilterCount'] = logGroup['metricFilterCount']
            log_dict['arn'] = logGroup['arn']
            log_dict['storedBytes'] = human_readable_bytes(logGroup['storedBytes'])
            log_dict['kmsKeyId'] = logGroup.get('kmsKeyId', None)
            log_dict['dataProtectionStatus'] = logGroup.get('dataProtectionStatus', None)
            log_dict['inheritedProperties'] = '\n'.join(map(str, logGroup.get('inheritedProperties', [])))
            log_dict['logGroupClass'] = logGroup['logGroupClass']
            log_dict['logGroupArn'] = logGroup.get('logGroupArn', None)
            # Print log group name and creation time
            print(logGroup['logGroupName'], " <> ", log_dict['creationTime'])
            # Append log group details to the list
            logs_list.append(log_dict)

# Create a DataFrame using pandas
df = pd.DataFrame(logs_list)

# Write the DataFrame to a CSV file
csv_filename = 'describe_log_groups.csv'
df.to_csv(os.path.join(directory, filename), index=False)
