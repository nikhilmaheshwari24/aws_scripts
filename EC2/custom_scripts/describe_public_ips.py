import boto3
import pandas as pd

""" This script retrieves information about network interfaces with public IP associations across multiple AWS regions and profiles. It can be used for auditing, monitoring, or managing public IP usage within an organization's AWS infrastructure. """

# List of regions to iterate over
regions = ['ap-southeast-1', 'us-east-1', 'ap-south-1']

# Create a session using default credentials
session = boto3.Session()

# Get available profiles from the session
profiles = session.available_profiles

# List to store public IP information
ip_list = []

# Iterate over each profile and region
for profile in profiles:

    for region in regions:
        # Create a session with the current profile
        profile_session = boto3.session.Session(profile_name=profile)
        
        # Create an EC2 client for the region
        ec2_client = profile_session.client('ec2', region_name=region)
        
        # Use a paginator to retrieve network interfaces
        paginator = ec2_client.get_paginator('describe_network_interfaces')
        net_interfaces_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
        
        # Iterate over each page of network interfaces
        for page in net_interfaces_paginator:
            # Iterate over each network interface
            for interface in page['NetworkInterfaces']:
                publicIp_dict = {}
                if 'Association' in interface.keys():
                    # Store public IP information
                    publicIp_dict['OwnerId'] = interface['OwnerId']
                    publicIp_dict['Region'] = region
                    publicIp_dict['NetworkInterfaceId'] = interface['NetworkInterfaceId']
                    publicIp_dict['InterfaceType'] = interface['InterfaceType']
                    publicIp_dict['PublicIP'] = interface['Association']['PublicIp']
                    # Fetching Vpc Cidr Blocks
                    vpc_response = ec2_client.describe_vpcs(VpcIds=[interface['VpcId']])
                    vpc_cidr=[]
                    if 'Vpcs' in vpc_response and len(vpc_response['Vpcs']) > 0:
                        vpc = vpc_response['Vpcs'][0]
                        cidr_block = vpc.get('CidrBlockAssociationSet', [])
                        for cidr in cidr_block:
                            if cidr['CidrBlockState']['State'] == 'associated':
                                vpc_cidr.append(cidr['CidrBlock'])
                    publicIp_dict['Cidr_Associated_With_Vpc'] = vpc_cidr                    
                    
                    # Print public IP information
                    print(interface['OwnerId'], interface['InterfaceType'], interface['Association']['PublicIp'], region)
                else:
                    # Skip network interfaces without public IP associations
                    continue

                # Append the dictionary to the list
                ip_list.append(publicIp_dict)

# Create a DataFrame from the list
df = pd.DataFrame(ip_list)

# Export the DataFrame to a CSV file
filename = "org_public_ips.csv"
df.to_csv(filename, index=False)
