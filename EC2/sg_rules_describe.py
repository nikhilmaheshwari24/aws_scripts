import boto3
import os
import csv
import sys
import pandas as pd

# Get the environment argument from the command line
env = str(sys.argv[1])

# Set the AWS profile environment variable
os.environ['AWS_PROFILE'] = env

# List of regions to iterate over
regions = ['us-east-1', 'ap-southeast-1', 'ap-south-1']

# Create an EC2 client
ec2 = boto3.client('ec2')

# List of security group IDs to retrieve information for
sg_id = ['']

# Describe security groups for the given security group IDs
sg = ec2.describe_security_groups(GroupIds=sg_id)

# List to store security group rule information
rulelist = []

# Iterate over each security group
for sg in sg['SecurityGroups']:
    for ipPermission in sg['IpPermissions']:
        for permission in ipPermission['IpRanges']:
            ruledict = {}
            if permission.get('Description') and ipPermission.get('FromPort'):
                # Store rule information for rules with description and from port
                ruledict['GroupId'] = sg['GroupId']
                ruledict['Port'] = ipPermission['FromPort']
                ruledict['Protocol'] = ipPermission['IpProtocol']
                ruledict['CIDR'] = permission['CidrIp']
                ruledict['Description'] = permission['Description']
            elif ipPermission.get('FromPort') == '-1' or ipPermission.get('IpProtocol') == '-1':
                # Store rule information for rules with all ports and protocols
                ruledict['GroupId'] = sg['GroupId']
                ruledict['Port'] = 'ALL'
                ruledict['Protocol'] = 'ALL'
                ruledict['CIDR'] = permission['CidrIp']
                ruledict['Description'] = permission['Description']
            else:
                # Store rule information for rules without description
                ruledict['GroupId'] = sg['GroupId']
                ruledict['Port'] = ipPermission['FromPort']
                ruledict['Protocol'] = ipPermission['IpProtocol']
                ruledict['CIDR'] = permission['CidrIp']
                ruledict['Description'] = "--"
            
            # Append the dictionary to the list
            rulelist.append(ruledict)

# Create a DataFrame from the list
df = pd.DataFrame(rulelist)

# Print the DataFrame
print(df)

# Export the DataFrame to a CSV file
filename = "sg-inbound-rules.csv"
df.to_csv(filename)
