import boto3
import os
import pandas as pd

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ""

# Define AWS regions
regions = ['us-east-2']

instances_list = []

def instance_tags(instance_tags_list):

    # Initialize an empty list to store tags
    tag_list = []
    
    # Process each tag and store it in the list
    for tag in instance_tags_list:
        key = tag['Key']
        value = tag['Value']
        tag_list.append(f"{key}: {value}")

    # Return the concatenated tags if tags are present
    if tag_list:
        return '\n'.join(tag_list)
    else:
        return "No Tags Available"

for region in regions:

    ec2_client = boto3.client('ec2',region_name=region)
    paginator = ec2_client.get_paginator('describe_instances')
    ec2_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})

    for page in ec2_paginator:

        for reservation in page['Reservations']:

            for instance in reservation['Instances']:

                instance_dict = {}

                instance_dict['AmiLaunchIndex'] = instance['AmiLaunchIndex']
                instance_dict['ImageId'] = instance['ImageId']
                instance_dict['InstanceId'] = instance['InstanceId']
                instance_dict['InstanceType'] = instance['InstanceType']
                instance_dict['KernelId'] = instance.get('KernelId', None)
                instance_dict['KeyName'] = instance.get('KeyName', None)
                instance_dict['LaunchTime'] = instance['LaunchTime']
                instance_dict['Monitoring'] = instance['Monitoring']['State']
                # instance_dict['Placement'] = instance['Placement']
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
                instance_dict['BlockDeviceMappings'] = '\n'.join(map(str,instance['BlockDeviceMappings']))
                instance_dict['ClientToken'] = instance['ClientToken']
                instance_dict['EbsOptimized'] = instance['EbsOptimized']
                instance_dict['EnaSupport'] = instance['EnaSupport']
                instance_dict['Hypervisor'] = instance['Hypervisor']
                instance_dict['IamInstanceProfile'] = instance.get('IamInstanceProfile', {}).get('Arn', None)
                instance_dict['InstanceLifecycle'] = instance.get('InstanceLifecycle', None)
                instance_dict['ElasticGpuAssociations'] = instance.get('ElasticGpuAssociations', {})
                instance_dict['ElasticInferenceAcceleratorAssociations'] = instance.get('ElasticInferenceAcceleratorAssociations', [])
                instance_dict['NetworkInterfaces'] = '\n'.join(map(str,instance['NetworkInterfaces']))
                instance_dict['OutpostArn'] = instance.get('OutpostArn', None)
                instance_dict['RootDeviceName'] = instance['RootDeviceName']
                instance_dict['RootDeviceType'] = instance['RootDeviceType']
                instance_dict['SecurityGroups'] = '\n'.join(map(str,instance['SecurityGroups']))
                instance_dict['SourceDestCheck'] = instance.get('SourceDestCheck', None)
                instance_dict['SpotInstanceRequestId'] = instance.get('SpotInstanceRequestId', None)
                instance_dict['SriovNetSupport'] = instance.get('SriovNetSupport', None)
                instance_dict['StateReason'] = instance.get('StateReason', {}).get('Message', None)
                instance_dict['Tags'] = instance_tags(instance.get('Tags', []))
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

                print(instance['InstanceId'])

                instances_list.append(instance_dict)
            
# Create a DataFrame using pandas
df = pd.DataFrame(instances_list)

# Write the DataFrame to a CSV file
csv_filename = 'describe_instances.csv'
df.to_csv(csv_filename, index=False)
