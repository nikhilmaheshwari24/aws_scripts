import boto3
import os
import pandas as pd

# Set AWS profile
os.environ['AWS_PROFILE'] = ''

# Create a directory for storing CSV files if it doesn't exist
directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

# Define AWS regions to search for Elastic IP addresses
regions = ['us-east-2']

# Initialize a list to store Elastic IP address information
addresses_list = []

# Function to extract resource name from tags
def get_resource_name(resource_tags_list):
    if resource_tags_list:
        for tag in resource_tags_list:
            if 'Name' == tag['Key']:
                return tag['Value']
    else:
        return None

# Function to concatenate resource tags
def resource_tags(resource_tags_list):
    # Initialize an empty list to store tags
    tag_list = []
    # Process each tag and store it in the list
    for tag in resource_tags_list:
        key = tag['Key']
        value = tag['Value']
        tag_list.append(f"{key}: {value}")
    # Return the concatenated tags if tags are present
    if tag_list:
        return '\n'.join(tag_list)
    else:
        return "No Tags Available"

# Iterate over each region
for region in regions:
    # Create an EC2 client for the region
    ec2_client = boto3.client('ec2', region_name=region)
    # Describe Elastic IP addresses
    addresses = ec2_client.describe_addresses()
    # Iterate over each Elastic IP address
    for address in addresses['Addresses']:
        address_dict = {}
        # Extract address details
        address_dict['Name'] = get_resource_name(address.get('Tags', []))
        address_dict['InstanceId'] = address.get('InstanceId', None)
        address_dict['PublicIp'] = address['PublicIp']
        address_dict['AllocationId'] = address['AllocationId']
        address_dict['AssociationId'] = address['AssociationId']
        address_dict['Domain'] = address['Domain']
        address_dict['NetworkInterfaceId'] = address['NetworkInterfaceId']
        address_dict['NetworkInterfaceOwnerId'] = address['NetworkInterfaceOwnerId']
        address_dict['PrivateIpAddress'] = address['PrivateIpAddress']
        address_dict['Tags'] = resource_tags(address.get('Tags', []))
        address_dict['PublicIpv4Pool'] = address['PublicIpv4Pool']
        address_dict['NetworkBorderGroup'] = address['NetworkBorderGroup']
        address_dict['CustomerOwnedIp'] = address.get('CustomerOwnedIp', None)
        address_dict['CustomerOwnedIpv4Pool'] = address.get('CustomerOwnedIpv4Pool', None)
        address_dict['CarrierIp'] = address.get('CarrierIp', None)
        # Append address details to the list
        addresses_list.append(address_dict)
        # Print address details
        print(address_dict['Name'], " <> ", address_dict['PublicIp'])

# Create a DataFrame from the list
df = pd.DataFrame(addresses_list)

# Export the DataFrame to a CSV file
filename = 'describe_addresses.csv'
df.to_csv(os.path.join(directory, filename), index=False)
