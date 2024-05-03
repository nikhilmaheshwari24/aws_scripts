import boto3
import os
import pandas as pd
from datetime import datetime, timezone

# Set AWS profile
os.environ['AWS_PROFILE'] = ''

# Create a directory for storing CSV files if it doesn't exist
directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

# Define AWS regions to search for images
regions = ['us-east-2']

# Initialize a list to store image information
images_list = []

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

# Function to calculate age of the image based on its creation date
def calculate_age(create_date):
    create_date = datetime.fromisoformat(str(create_date)).astimezone(timezone.utc)
    today = datetime.now(timezone.utc)
    age = today - create_date
    return age.days

# Iterate over each region
for region in regions:
    # Create an EC2 client for the region
    ec2_client = boto3.client('ec2', region_name=region)
    # Describe images owned by self
    paginator = ec2_client.get_paginator('describe_images')
    images_paginator = paginator.paginate(Owners=['self'])
    # Iterate over each page of images
    for page in images_paginator:
        # Iterate over each image
        for image in page['Images']:
            image_dict = {}
            # Extract image details
            image_dict['Name'] = get_resource_name(image.get('Tags', []))
            image_dict['Architecture'] = image['Architecture']
            image_dict['CreationDate'] = image['CreationDate']
            image_dict['ImageAge'] = calculate_age(image['CreationDate'])
            image_dict['ImageId'] = image['ImageId']
            image_dict['ImageLocation'] = image['ImageLocation']
            image_dict['ImageType'] = image['ImageType']
            image_dict['Public'] = image.get('Public', None)
            image_dict['OwnerId'] = image.get('OwnerId', None)
            image_dict['Platform'] = image.get('Platform', None)
            image_dict['PlatformDetails'] = image.get('PlatformDetails', None)
            image_dict['UsageOperation'] = image.get('UsageOperation', None)
            # Extract product code details
            product_codes = image.get('ProductCodes', [])
            if product_codes:
                image_dict['ProductCodes_ProductCodeId'] = product_codes[0].get('ProductCodeId')
                image_dict['ProductCodes_ProductCodeType'] = product_codes[0].get('ProductCodeType')
            else:
                image_dict['ProductCodes_ProductCodeId'] = None
                image_dict['ProductCodes_ProductCodeType'] = None
            image_dict['RamdiskId'] = image.get('RamdiskId', None)
            image_dict['State'] = image.get('State')
            image_dict['BlockDeviceMappings'] = '\n'.join(map(str, image.get('BlockDeviceMappings', [])))
            image_dict['Description'] = image.get('Description', None)
            image_dict['EnaSupport'] = image.get('EnaSupport', None)
            image_dict['Hypervisor'] = image.get('Hypervisor', None)
            image_dict['ImageOwnerAlias'] = image.get('ImageOwnerAlias', None)
            image_dict['RootDeviceName'] = image.get('RootDeviceName', None)
            image_dict['RootDeviceType'] = image.get('RootDeviceType', None)
            image_dict['SriovNetSupport'] = image.get('SriovNetSupport', None)
            image_dict['StateReason'] = image.get('StateReason', None)
            image_dict['Tags'] = image.get('Tags', [])
            image_dict['VirtualizationType'] = image['VirtualizationType']
            image_dict['BootMode'] = image.get('BootMode', None)
            image_dict['TpmSupport'] = image.get('TpmSupport', None)
            image_dict['DeprecationTime'] = image.get('DeprecationTime', None)
            image_dict['ImdsSupport'] = image.get('ImdsSupport', None)
            image_dict['SourceInstanceId'] = image['SourceInstanceId']
            image_dict['DeregistrationProtection'] = image.get('DeregistrationProtection', None)
            image_dict['LastLaunchedTime'] = image.get('LastLaunchedTime', None)
            # Append image details to the list
            images_list.append(image_dict)
            # Print image details
            print(image_dict['Name'], " <> ", image_dict['ImageId'])

# Create DataFrame
df = pd.DataFrame(images_list)

# Write DataFrame to CSV file
filename = 'describe_images.csv'
df.to_csv(os.path.join(directory, filename), index=False)
