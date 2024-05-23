import boto3
import os
import pandas as pd
from botocore.exceptions import ClientError

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define a directory to store CSV files
directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

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

    for instance_id in instance_ids:
        try:
            # Paginate through instances
            instances_paginator = ec2_paginator.paginate(InstanceIds=[instance_id])
            # Iterate through each page of instances
            for page in instances_paginator:
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        # Extract instance details
                        state = instance['State']['Name']
                        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        name = tags.get('Name', 'N/A')
                        # Append instance details to the list
                        instance_info.append({'Instance ID': instance_id, 'State': state, 'Name': name})
                        
                        print(instance_id, "-", state, "::", name)

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                # print(f"Instance ID not found: {e.response['Error']['Message']}")
                # Append instance details to the list
                instance_info.append({'Instance ID': instance_id, 'State': e.response['Error']['Message'], 'Name': ""})

                print(instance_id, "-", e.response['Error']['Message'], "::", "")

            else:
                # print(f"Unexpected error: {e}")
                instance_info.append({'Instance ID': instance_id, 'State': str(e), 'Name': ""})

                print(instance_id, "-", e, "::", "")

# Create a DataFrame using pandas
df = pd.DataFrame(instance_info)

# Write the DataFrame to a CSV file
filename = 'instance_name_state.csv'
df.to_csv(os.path.join(directory, filename), index=False)

print("Script execution completed. CSV file saved as:", os.path.join(directory, filename))
