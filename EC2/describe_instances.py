import boto3
import os
import pandas as pd
from datetime import datetime, timezone

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define AWS regions to search for instances
regions = ['us-east-2']

# Initialize a list to store instance information
instances_list = []

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
    # Describe instances
    paginator = ec2_client.get_paginator('describe_instances')
    ec2_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})
    # Iterate over each page of instances
    for page in ec2_paginator:
        # Iterate over each reservation
        for reservation in page['Reservations']:
            # Iterate over each instance
            for instance in reservation['Instances']:
                instance_dict = {}
                # Extract instance details
                instance_dict['AmiLaunchIndex'] = instance['AmiLaunchIndex']
                instance_dict['ImageId'] = instance['ImageId']
                instance_dict['InstanceId'] = instance['InstanceId']
                instance_dict['InstanceType'] = instance['InstanceType']
                instance_dict['KernelId'] = instance.get('KernelId', None)
                instance_dict['KeyName'] = instance.get('KeyName', None)
                instance_dict['LaunchTime'] = instance['LaunchTime']
                instance_dict['Age'] = calculate_age(instance['LaunchTime'])
                instance_dict['Monitoring'] = instance['Monitoring']['State']
                instance_dict['Placement_AvailabilityZone'] = instance['Placement']['AvailabilityZone']
                instance_dict['Placement_Tenancy'] = instance['Placement']['Tenancy']
                instance_dict['Platform'] = instance.get('Platform', None)
                instance_dict['PrivateDnsName'] = instance['PrivateDnsName']
                instance_dict['PrivateIpAddress'] = instance.get('PrivateIpAddress', None)
                instance_dict['PrivateIpAddresses'] = instance.get('PrivateIpAddresses', {})
                product_codes = instance.get('ProductCodes', [])
                if product_codes:
                    instance_dict['ProductCodes_ProductCodeId'] = product_codes[0].get('ProductCodeId', None)
                    instance_dict['ProductCodes_ProductCodeType'] = product_codes[0].get('ProductCodeType', None)
                else:
                    instance_dict['ProductCodes_ProductCodeId'] = None
                    instance_dict['ProductCodes_ProductCodeType'] = None
                instance_dict['PublicDnsName'] = instance['PublicDnsName']
                instance_dict['PublicIpAddress'] = instance.get('PublicIpAddress', None)
                instance_dict['RamdiskId'] = instance.get('RamdiskId', None)
                instance_dict['State'] = instance['State']['Name']
                instance_dict['StateTransitionReason'] = instance['StateTransitionReason']
                instance_dict['SubnetId'] = instance.get('SubnetId', None)
                instance_dict['VpcId'] = instance.get('VpcId', None)
                instance_dict['Architecture'] = instance['Architecture']
                instance_dict['BlockDeviceMappings'] = '\n'.join(map(str, instance['BlockDeviceMappings']))
                instance_dict['ClientToken'] = instance['ClientToken']
                instance_dict['EbsOptimized'] = instance['EbsOptimized']
                instance_dict['EnaSupport'] = instance['EnaSupport']
                instance_dict['Hypervisor'] = instance['Hypervisor']
                instance_dict['IamInstanceProfile'] = instance.get('IamInstanceProfile', {}).get('Arn', None)
                instance_dict['InstanceLifecycle'] = instance.get('InstanceLifecycle', None)
                instance_dict['ElasticGpuAssociations'] = instance.get('ElasticGpuAssociations', {})
                instance_dict['ElasticInferenceAcceleratorAssociations'] = instance.get('ElasticInferenceAcceleratorAssociations', [])
                instance_dict['NetworkInterfaces'] = '\n'.join(map(str, instance['NetworkInterfaces']))
                instance_dict['OutpostArn'] = instance.get('OutpostArn', None)
                instance_dict['RootDeviceName'] = instance['RootDeviceName']
                instance_dict['RootDeviceType'] = instance['RootDeviceType']
                instance_dict['SecurityGroups'] = '\n'.join(map(str, instance['SecurityGroups']))
                instance_dict['SourceDestCheck'] = instance.get('SourceDestCheck', None)
                instance_dict['SpotInstanceRequestId'] = instance.get('SpotInstanceRequestId', None)
                instance_dict['SriovNetSupport'] = instance.get('SriovNetSupport', None)
                instance_dict['StateReason'] = instance.get('StateReason', {}).get('Message', None)
                instance_dict['Tags'] = resource_tags(instance.get('Tags', []))
                instance_dict['VirtualizationType'] = instance['VirtualizationType']
                instance_dict['CpuOptions'] = instance['CpuOptions']
                instance_dict['CapacityReservationId'] = instance.get('CapacityReservationId', None)
                instance_dict['CapacityReservationSpecification'] = instance['CapacityReservationSpecification']
                instance_dict['HibernationOptions'] = instance['HibernationOptions']['Configured']
                instance_dict['Licenses'] = instance.get('Licenses', [])
                instance_dict['MetadataOptions'] = instance['MetadataOptions']
                instance_dict['EnclaveOptions'] = instance['EnclaveOptions']['Enabled']
                instance_dict['BootMode'] = instance.get('BootMode', None)
                instance_dict['PlatformDetails'] = instance['PlatformDetails']
                instance_dict['UsageOperation'] = instance['UsageOperation']
                instance_dict['UsageOperationUpdateTime'] = instance['UsageOperationUpdateTime']
                instance_dict['PrivateDnsNameOptions'] = instance.get('PrivateDnsNameOptions', None)
                instance_dict['Ipv6Address'] = instance.get('Ipv6Address', None)
                instance_dict['TpmSupport'] = instance.get('TpmSupport', None)
                instance_dict['MaintenanceOptions'] = instance['MaintenanceOptions']['AutoRecovery']
                instance_dict['CurrentInstanceBootMode'] = instance.get('CurrentInstanceBootMode', None)
                # Append instance details to the list
                instances_list.append(instance_dict)
                # Print instance ID
                print(instance['InstanceId'])

# Create a DataFrame using pandas
df = pd.DataFrame(instances_list)

# Write the DataFrame to a CSV file
filename = 'describe_instances.csv'
df.to_csv(os.path.join(directory, filename), index=False)
