import boto3
import os
import pandas as pd

# Set AWS profile
os.environ['AWS_PROFILE'] = ''

# Define AWS regions
regions = ['us-east-2']

# List to store network interface details
network_interfaces_list = []

# Iterate through each region
for region in regions:
        
    # Create EC2 client for the region
    ec2_client = boto3.client('ec2', region_name=region)
    
    # Paginate through network interfaces
    paginator = ec2_client.get_paginator('describe_network_interfaces')
    network_interfaces_paginator = paginator.paginate(PaginationConfig={'PageSize': 123})

    # Iterate through each page of network interfaces
    for network_interfaces_page in network_interfaces_paginator:
        
        # Iterate through each network interface
        for interface in network_interfaces_page['NetworkInterfaces']:

            # Dictionary to store network interface details
            network_interfaces_dict = {}
            
            # Basic details
            network_interfaces_dict['Region'] = region
            network_interfaces_dict['NetworkInterfaceId'] = interface['NetworkInterfaceId']
            network_interfaces_dict['Status'] = interface['Status']
            network_interfaces_dict['Description'] = interface['Description']
            network_interfaces_dict['InterfaceType'] = interface['InterfaceType']
            network_interfaces_dict['VpcId'] = interface['VpcId']
            network_interfaces_dict['SubnetId'] = interface['SubnetId']
            network_interfaces_dict['AvailabilityZone'] = interface['AvailabilityZone']

            # Connection tracking configuration
            connection_tracking = interface.get('ConnectionTrackingConfiguration', {})
            connection_tracking_str = '\n'.join(f"{key}: {value}" for key, value in connection_tracking.items())
            network_interfaces_dict['ConnectionTrackingConfiguration'] = connection_tracking_str

            # More basic details
            network_interfaces_dict['Description'] = interface['Description']
            network_interfaces_dict['OwnerId'] = interface['OwnerId']
            network_interfaces_dict['MacAddress'] = interface['MacAddress']
            network_interfaces_dict['PrivateIpAddress'] = interface['PrivateIpAddress']
            network_interfaces_dict['PrivateDnsName'] = interface['PrivateDnsName']
            
            # IP prefixes
            network_interfaces_dict['Ipv4Prefixes'] = '\n'.join(interface.get('Ipv4Prefixes', []))
            network_interfaces_dict['Ipv6Prefixes'] = '\n'.join(interface.get('Ipv6Prefixes', []))

            # Private IP addresses
            private_ip_addresses = [private_ip_address['PrivateIpAddress'] for private_ip_address in interface['PrivateIpAddresses']]
            network_interfaces_dict['PrivateIpAddresses'] = '\n'.join(private_ip_addresses)

            # Security groups
            security_groups_ids = [security_group['GroupId'] for security_group in interface['Groups']]
            network_interfaces_dict['SecurityGroupId'] = '\n'.join(security_groups_ids)

            # Association details
            association_info = interface.get('Association', 'N/A')
            network_interfaces_dict['Association'] = '\n'.join([f"{key}={value}" for key, value in association_info.items()])

            # Attachment details
            attachment_info = interface.get('Attachment', 'N/A')
            network_interfaces_dict['Attachment'] = ', '.join([f"{key}={value}" for key, value in attachment_info.items()])

            # Tags
            tagset = [f"{tag['Key']}={tag['Value']}" for tag in interface.get('TagSet', [])]
            network_interfaces_dict['Tags'] = '\n'.join(tagset) if tagset else 'N/A'

            # Print network interface details
            print(interface['NetworkInterfaceId'], interface['InterfaceType'], interface['Status']))

            # Append network interface details to the list
            network_interfaces_list.append(network_interfaces_dict)

# Create DataFrame from the list of network interface details
dataframe = pd.DataFrame(network_interfaces_list)

# Save DataFrame to a CSV file
filename = "NAT_Gateways.csv"
dataframe.to_csv(filename, index=False)
