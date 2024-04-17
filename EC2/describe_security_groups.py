import boto3
import os
import pandas as pd

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ""

# Define AWS regions to search for RDS snapshots
regions = ['us-east-1']

# Initialize an empty list to store security group details
security_group_info = []

# Iterate over each AWS region
for region in regions:

    # Create an EC2 client for the specified region
    ec2_client = boto3.client('ec2', region_name=region)

    # Initialize a paginator for describe_security_groups operation
    paginator = ec2_client.get_paginator('describe_security_groups')

    # Paginate through security groups
    for page in paginator.paginate():

        # Extract security groups from the response
        security_groups = page['SecurityGroups']

        # Iterate through each security group
        for sg in security_groups:

            # Initialize a dictionary to store details of the current security group
            sg_details = {}

            # Assign values to dictionary keys
            sg_details['GroupId'] = sg['GroupId']
            sg_details['GroupName'] = sg['GroupName']
            sg_details['Description'] = sg['Description']
            sg_details['VpcId'] = sg['VpcId']

            # Initialize an empty list to store inbound rules for the security group
            inbound_rules = []

            # Extract inbound rules from the security group
            for permission in sg['IpPermissions']:
                for ip_range in permission.get('IpRanges', []):
                    inbound_rule = {
                        'FromPort': permission.get('FromPort'),
                        'ToPort': permission.get('ToPort'),
                        'Protocol': permission['IpProtocol'],
                        'CIDR': ip_range['CidrIp'],
                        'Description': ip_range.get('Description', 'N/A')
                    }
                    inbound_rules.append(inbound_rule)

            # Add inbound rules to the security group details
            sg_details['InboundRules'] = '\n'.join(map(str, inbound_rules))

            # Extract tags from the security group
            tags = [{tag['Key']: tag['Value']} for tag in sg.get('Tags', [])]

            # Add tags to the security group details
            sg_details['Tags'] = '\n'.join(map(str, tags))

            # Append the details of the current security group to the list
            security_group_info.append(sg_details)

# Create a DataFrame using pandas
df = pd.DataFrame(security_group_info)

# Write the DataFrame to a CSV file
csv_filename = 'security_groups_describe.csv'
df.to_csv(csv_filename, index=False)
