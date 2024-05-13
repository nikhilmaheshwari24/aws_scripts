import boto3
import os
from datetime import datetime, timedelta
import pandas as pd
import botocore

# Set AWS profile
os.environ["AWS_PROFILE"] = ""

directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

# List of S3 buckets
buckets = []

# Create an S3 client
s3_client = boto3.client('s3')

# Converts Bytes to Human Readable Format
def human_readable_bytes(value):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    
    while value >= 1000 and unit_index < len(units) - 1:
        value /= 1000
        unit_index += 1

    return f"{value:.2f}{units[unit_index]}"

# Figure out Bucket Region
def bucket_region(bucket):
    region = s3_client.get_bucket_location(Bucket=bucket)['LocationConstraint']
    if region is None or region == "N.Virginia":
        region = "us-east-1"
    else:
        region
    return region

# Calculate Bucket Size
def bucket_size(bucket, region):

    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Define time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)  # 14 days ago

    # Format start and end times as strings
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')

    # List of storage types to iterate over
    storage_types = [
        'StandardStorage', 'IntelligentTieringFAStorage', 'IntelligentTieringIAStorage',
        'IntelligentTieringAAStorage', 'IntelligentTieringAIAStorage', 'IntelligentTieringDAAStorage',
        'StandardIAStorage', 'StandardIASizeOverhead', 'StandardIAObjectOverhead', 'OneZoneIAStorage',
        'OneZoneIASizeOverhead', 'ReducedRedundancyStorage', 'GlacierInstantRetrievalSizeOverhead',
        'GlacierInstantRetrievalStorage', 'GlacierStorage', 'GlacierStagingStorage', 'GlacierObjectOverhead',
        'GlacierS3ObjectOverhead', 'DeepArchiveStorage', 'DeepArchiveObjectOverhead',
        'DeepArchiveS3ObjectOverhead', 'DeepArchiveStagingStorage', 'ExpressOneZone'
    ]

    # Iterate over storage types
    for storage_type in storage_types:
        # Get metric data for the current storage type
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='BucketSizeBytes',
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket},
                {'Name': 'StorageType', 'Value': storage_type}
            ],
            StartTime=start_time_str,
            EndTime=end_time_str,
            Period=86400,
            Statistics=['Maximum'],
            Unit='Bytes'
        )

        # Check if datapoints exist
        if 'Datapoints' in response:
            datapoints = response['Datapoints']
            if datapoints:
                # Assuming there's only one data point, retrieve its maximum value
                return human_readable_bytes(int(datapoints[0]['Maximum']))

    return None

# Calculate Object Count
def bucket_objects_count(bucket, region):

    cloudwatch = boto3.client('cloudwatch', region_name=region)

    # Define time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)  # 14 days ago

    # Format start and end times as strings
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')

    # Get metric data
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='NumberOfObjects',
        Dimensions=[
            {'Name': 'BucketName', 'Value': bucket},
            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
        ],
        StartTime=start_time_str,
        EndTime=end_time_str,
        Period=86400,
        Statistics=['Maximum'],
        Unit='Count'
    )

    # Extract the maximum number of objects
    if 'Datapoints' in response:
        datapoints = response['Datapoints']
        if datapoints:
            # Assuming there's only one data point, retrieve its maximum value
            return int(datapoints[0]['Maximum'])

    return None

# Check Bucket Versioning
def bucket_versioning(bucket):
    versioning = s3_client.get_bucket_versioning(Bucket=bucket).get("Status", None)
    if versioning == "Enabled":
        return "Enabled"
    else:
        return "Disabled"

# Checks if Bucket is Empty or not
def bucket_object_list(bucket):

    response = s3_client.list_objects(Bucket=bucket)

    if 'Contents' in response:
        length = len(response['Contents'])
        if length == 0:
            return "Empty"
        else:
            return "Not Empty"
    else:
        return "Empty"

# Checks Tags on the Bucket
def bucket_tags(bucket):
    try:
        # Initialize an empty list to store tags
        tag_list = []

        # Retrieve bucket tagging information
        response = s3_client.get_bucket_tagging(Bucket=bucket)

        # Check if tags are present in the response
        tag_set = response.get('TagSet', [])

        # Process each tag and store it in the list
        for tag in tag_set:
            key = tag['Key']
            value = tag['Value']
            tag_list.append(f"{key}: {value}")

        # Return the concatenated tags if tags are present
        if tag_list:
            return '\n'.join(tag_list)
        else:
            return "No Tags Available"
    
    except Exception as e:
        return f"Error retrieving tags: {str(e)}"

# Check Lifecycle Policy on Bucket
def bucket_lifecycle(bucket):
    try:
        response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket)
        lifecycle_rules = response.get('Rules', [])
        
        # Check if rules are present
        if lifecycle_rules:
            # Process each rule
            lifecycle_policy_list = []
            for rule in lifecycle_rules:
                lifecycle_policy_dict = {
                    'ID': rule.get('ID', 'N/A'),
                    'Status': rule.get('Status', 'N/A'),
                    'FilterPrefix': rule.get('Filter', {}).get('Prefix', 'N/A'),
                    'Transitions': rule.get('Transitions', 'N/A'),
                    'Expiration': rule.get('Expiration', 'N/A')
                }
                lifecycle_policy_list.append(lifecycle_policy_dict)

            return lifecycle_policy_list  # Return the list of dictionaries
        else:
            return []  # Return an empty list if no rules are present
    
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == 'NoSuchLifecycleConfiguration':
            return []  # Return an empty list if no lifecycle configuration is found
        else:
            raise f"Error retrieving lifecycle policy: {str(e)}"

# Get Public Access Block
def get_public_access_block(bucket):
    try:
        response = s3_client.get_public_access_block(Bucket=bucket)
        
        public_access_block_config = response.get('PublicAccessBlockConfiguration', {})
        
        result = ', '.join([f"'{key}': {value}" for key, value in public_access_block_config.items()])
        
        return result
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
            return "Not Configured"
        else:
            raise e

# Get Ownership Controls
def get_ownership_controls(bucket):
    try:
        response = s3_client.get_bucket_ownership_controls(Bucket=bucket)
        
        ownership_controls = response.get('OwnershipControls', {})
        rules = ownership_controls.get('Rules', [])
        
        rule_values = [rule.get('ObjectOwnership', 'N/A') for rule in rules]
        
        return ', '.join(rule_values)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'OwnershipControlsNotFoundError':
            return "Not Configured"
        else:
            raise e

# Get Bucket Policy
def get_bucket_policy(bucket):
    try:
        response = s3_client.get_bucket_policy(Bucket=bucket)
        return response.get('Policy', 'Policy Not Found')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return "Policy Not Found"
        else:
            raise e

# Check if the Bucket has Static Web Hosting enabled or not
def check_static_web_hosting(bucket):
    try:
        response = s3_client.get_bucket_website(Bucket=bucket)
        return True
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchWebsiteConfiguration':
            return False
        else:
            raise e

# Get Bucket Request Payment
def get_bucket_request_payment(bucket):
    response = s3_client.get_bucket_request_payment(Bucket=bucket)
    payer = response['Payer']
    return payer

# Check if the bucket is enabled for bucket notification configuration
def check_event_notification(bucket_name):
    try:
        response = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
        return "Enabled" if response else "Disabled"
    except Exception as e:
        return str(e)
    
# Check if Cross-Origin Resource Sharing is enabled or not
def check_cors(bucket_name):
    try:
        response = s3_client.get_bucket_cors(Bucket=bucket_name)
        return "Enabled" if response['CORSRules'] else "Disabled"
    except Exception as e:
        return str(e)

# Check Server Access Logging
def check_server_access_logging(bucket_name):
    try:
        response = s3_client.get_bucket_logging(Bucket=bucket_name)
        return 'Enabled' if 'LoggingEnabled' in response else 'Disabled'
    except Exception as e:
        return str(e)

# Check Transfer Acceleraion
def check_transfer_acceleration(bucket_name):
    try:
        response = s3_client.get_bucket_accelerate_configuration(Bucket=bucket_name)
        return response.get('Status', 'Not Configured')
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == 'NoSuchBucket':
            return "Bucket Not Found"
        elif error_code == 'TransferAccelerationConfigurationNotFoundError':
            return "Not Configured"
        else:
            return str(e)

# Get Replication Bucket Name
def get_replication_bucket_name(bucket_name):
    try:
        response = s3_client.get_bucket_replication(Bucket=bucket_name)
        return response['ReplicationConfiguration']['Rules'][0]['Destination']['Bucket']
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == 'ReplicationConfigurationNotFoundError':
            return "Not Configured"
        else:
            return str(e)


# List to hold bucket information
bucket_list = []

# Loop through each bucket
for bucket in buckets:

    s3_client = boto3.client('s3')
    
    try:
        # Check if the bucket exists
        s3_client.head_bucket(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404':
            print(f"Bucket '{bucket}' does not exist. Skipping...")
            continue
        else:
            print(f"An error occurred while checking bucket '{bucket}': {error_code}. Skipping...")
            continue
    
    # If the code reaches this point, it means the bucket exists
    bucket_dict = {}
    bucket_dict['BucketName'] = bucket
    bucket_dict['BucketRegion'] = bucket_region(bucket)
    bucket_dict['BucketSize'] = bucket_size(bucket, bucket_dict['BucketRegion'])
    bucket_dict['NumberOfObjects'] = bucket_objects_count(bucket, bucket_dict['BucketRegion'])
    bucket_dict['BucketEmpty?'] = bucket_object_list(bucket)
    bucket_dict['BucketVersioning'] = bucket_versioning(bucket)
    bucket_dict['Tags'] = bucket_tags(bucket)
    
    # Get bucket lifecycle configuration
    lifecycle_rules = bucket_lifecycle(bucket)
    
    # Extract lifecycle policy information
    lifecycle_policy_list = []
    for rule in lifecycle_rules:
        lifecycle_policy_dict = {
            'ID': rule.get('ID', 'N/A'),
            'Status': rule.get('Status', 'N/A'),
            'FilterPrefix': rule.get('Filter', {}).get('Prefix', 'N/A'),
            'Transitions': rule.get('Transitions', 'N/A'),
            'Expiration': rule.get('Expiration', 'N/A')
        }
        lifecycle_policy_list.append(lifecycle_policy_dict)

    bucket_dict['Lifecycle'] = '\n'.join(map(str, lifecycle_policy_list))

    # Additional bucket information using custom functions
    bucket_dict['PublicAccessBlock'] = get_public_access_block(bucket)
    bucket_dict['OwnershipControls'] = get_ownership_controls(bucket)
    bucket_dict['BucketPolicy'] = get_bucket_policy(bucket)
    bucket_dict['StaticWebHosting'] = check_static_web_hosting(bucket)
    bucket_dict['RequestPayment'] = get_bucket_request_payment(bucket)
    bucket_dict['EventNotification'] = check_event_notification(bucket)
    bucket_dict['CORS'] = check_cors(bucket)
    bucket_dict['ServerAccessLogging'] = check_server_access_logging(bucket)
    bucket_dict['TransferAcceleration'] = check_transfer_acceleration(bucket)
    bucket_dict['ReplicationBucketName'] = get_replication_bucket_name(bucket)

    bucket_list.append(bucket_dict)

    print(bucket_dict['BucketName'], "<>", bucket_dict['BucketSize'], " <> ", bucket_dict['NumberOfObjects'] )

# Create a DataFrame using pandas
df = pd.DataFrame(bucket_list)

# Write the DataFrame to a CSV file
filename = 'selected_s3_bucket_info.csv'
df.to_csv(os.path.join(directory, filename), index=False)

print("Script execution completed. CSV file saved as:", os.path.join(directory, filename))
