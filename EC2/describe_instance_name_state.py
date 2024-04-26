import boto3
import os
import pandas as pd

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Input instance IDs separated by commas
instance_ids = []

# Define AWS regions to search for instances
regions = ['us-east-2']

# Initialize an empty list to store instance details
instance_info = []

# Iterate over each AWS region
for region in regions:

    # Create an EC2 client for the specified region
    ec2_client = boto3.client('ec2', region_name=region)

    # Initialize a paginator for describe_instances operation
    ec2_paginator = ec2_client.get_paginator('describe_instances')

    # Paginate through instances
    instances_paginator = ec2_paginator.paginate(InstanceIds=instance_ids)
    
    # Iterate through each page of instances
    for page in instances_paginator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                # Extract instance details
                instance_id = instance['InstanceId']
                state = instance['State']['Name']
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                name = tags.get('Name', 'N/A')
                
                # Append instance details to the list
                instance_info.append({'Instance ID': instance_id, 'State': state, 'Name': name})

# Create a DataFrame using pandas
df = pd.DataFrame(instance_info)

# Write the DataFrame to a CSV file
csv_filename = 'instance_name_state.csv'
df.to_csv(csv_filename, index=False)
