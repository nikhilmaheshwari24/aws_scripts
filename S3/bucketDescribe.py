import boto3
import csv
import os
from botocore.config import Config

# Retrieve the environment from command line arguments
environment = os.sys.argv[1]
os.environ['AWS_PROFILE'] = environment

# Create an S3 client
s3 = boto3.client('s3')

# Retrieve the list of existing buckets
response = s3.list_buckets()

# Initialize the final list and header for CSV
bucket_info_list = [{}]
csv_header = ['Name', 'CreationDate', 'Region', 'isEmpty', 'BucketVersioning', 'Access', 'Lifecycle', 'OwnershipControls', 'BucketPolicy', 'StaticWebHosting', 'RequesterPays', 'EventNotification', 'CrossOriginResourceSharing(CORS)', 'AccessPoints', 'ServerAccessLogging', 'TransferAcceleration', 'ReplicationBucketName', 'Tags']

# Output the bucket information
for bucket in response['Buckets']:
    # Create a dictionary to store information for the current bucket
    bucket_info = {}
    print(bucket["Name"])

    # Basic bucket information
    bucket_info['Name'] = bucket["Name"]
    bucket_info['CreationDate'] = bucket["CreationDate"]
    
    # Get the region where the bucket is located
    try:
        region = s3.get_bucket_location(Bucket=bucket["Name"])['LocationConstraint']
        bucket_info['Region'] = "us-east-1" if (region is None or region == "N. Virginia") else region
    except:
        bucket_info['Region'] = 'No permission'
    
    # Check if the bucket has any objects
    try:
        count_of_objects = len(s3.list_objects(Bucket=bucket["Name"])['Contents'])
        bucket_info['isEmpty'] = "NO"
    except:
        bucket_info['isEmpty'] = "YES"
    
    # Get Versioning status of the bucket
    try:
        bucket_info['Bucket Versioning'] = s3.get_bucket_versioning(Bucket=bucket["Name"])['Status']
    except:
        bucket_info['Bucket Versioning'] = '-'
    
    # Get public access block configuration
    try:
        if not s3.get_public_access_block(Bucket=bucket["Name"])['PublicAccessBlockConfiguration']['BlockPublicPolicy']:
            bucket_info['Access'] = "Objects can be public"
        else:
            bucket_info['Access'] = "Bucket and objects not public"
    except Exception as e:
        if str(e) == "An error occurred (AccessDenied) when calling the GetPublicAccessBlock operation: Access Denied":
            bucket_info['Access'] = "Error"
        else:
            bucket_info['Access'] = "Objects can be public"
    
    # Get status of Bucket Lifecycle Configuration
    try:
        life = s3.get_bucket_lifecycle_configuration(Bucket=bucket["Name"])
        bucket_info['Lifecycle'] = life['Rules'][0]['Status']
    except:
        bucket_info['Lifecycle'] = "-"
    
    # Bucket Ownership Controls - Bucket Owner Enforced, Bucket Owner Preferred, or Object Writer
    try:
        owner = s3.get_bucket_ownership_controls(Bucket=bucket["Name"])
        bucket_info['Ownership Controls'] = owner['OwnershipControls']['Rules'][0]['ObjectOwnership']
    except Exception as e:
        if str(e) == "An error occurred (AccessDenied) when calling the GetBucketOwnershipControls operation: Access Denied":
            bucket_info['Ownership Controls'] = "No Permission"
        else:
            bucket_info['Ownership Controls'] = "ObjectWriter"
    
    # Check if bucket policy is enabled or not
    try:
        policy = s3.get_bucket_policy(Bucket=bucket["Name"])
        bucket_info['Bucket Policy'] = "Enabled"
    except:
        bucket_info['Bucket Policy'] = "-"
    
    # Check if the bucket has Static Web Hosting enabled or not
    try:
        web = s3.get_bucket_website(Bucket=bucket["Name"])
        bucket_info['Static Web Hosting'] = "Enabled"
    except:
        bucket_info['Static Web Hosting'] = "-"
    
    # Check if Requester Pays is enabled or not, and if enabled then get the requester pays configuration
    try:
        rqpays = s3.get_bucket_request_payment(Bucket=bucket["Name"])
        bucket_info['Requester Pays'] = rqpays['Payer']
    except:
        bucket_info['Requester Pays'] = "-"
    
    # Check if the bucket is enabled for bucket notification configuration
    try:
        event = s3.get_bucket_notification_configuration(Bucket=bucket["Name"])
        bucket_info['Event Notification'] = "Enabled" if len(event) > 1 else "Disabled"
    except:
        bucket_info['Event Notification'] = "-"
    
    # Check if Cross-Origin Resource Sharing is enabled or not
    try:
        cors = s3.get_bucket_cors(Bucket=bucket["Name"])
        bucket_info['Cross Origin Resource Sharing'] = "Enabled"
    except:
        bucket_info['Cross Origin Resource Sharing'] = "-"
    
    # To check if the access point is enabled, we need to give account ID and region name as arguments
    if bucket_info['Region'] != 'No permission':
        conf = Config(region_name=bucket_info['Region'])
        s3control = boto3.client('s3control', config=conf)
        
        # Check if the access point is enabled for the specific bucket
        try:
            res = s3control.list_access_points(AccountId=acc['Account'], Bucket=bucket["Name"])
            bucket_info['Access Points'] = 'Enabled' if len(res['AccessPointList']) > 0 else '-'
        except:
            bucket_info['Access Points'] = 'Error'
    else:
        bucket_info['Access Points'] = 'Error'
    
    # Check if the server access logging is enabled or not
    try:
        if s3.get_bucket_logging(Bucket=bucket["Name"]).has_key('LoggingEnabled'):
            bucket_info['Server Access Logging'] = "Enabled"
        else:
            bucket_info['Server Access Logging'] = "Disabled"
    except:
        bucket_info['Server Access Logging'] = "-"
    
    # Get bucket status for Transfer Acceleration
    try:
        transfer_acc = s3.get_bucket_accelerate_configuration(Bucket=bucket["Name"])
        bucket_info['Transfer Acceleration'] = transfer_acc['Status']
    except:
        bucket_info['Transfer Acceleration'] = "-"
    
    # Get where the bucket will be replicated if any bucket is assigned in replication rules
    try:
        bucket_info['Replication Bucket Name'] = s3.get_bucket_replication(Bucket=bucket["Name"])['ReplicationConfiguration']['Rules'][0]['Destination']['Bucket']
    except:
        bucket_info['Replication Bucket Name'] = "-"
    
    # Get bucket tagging
    try:
        tag = s3.get_bucket_tagging(Bucket=bucket["Name"])['TagSet']
        tag_list = []

        for tag_entry in tag:
            # Create a string for each key-value pair
            tag_list.append(f"{tag_entry['Key']}: {tag_entry['Value']}")

        # Concatenate all key-value pairs with '\n' separator
        bucket_info['Tags'] = '\n'.join(tag_list)

    except:
        bucket_info['Tags'] = ""
    
    # Append the dictionary to the final list
    bucket_info_list.append(bucket_info)

# Output the length of the final list
print(len(bucket_info_list))

# Write the final list to a CSV file
filename = "AWS-Buckets.csv"
with open(filename, 'w') as csvfile:
    csvwriter = csv.DictWriter(csvfile, fieldnames=csv_header)
    csvwriter.writeheader()
    csvwriter.writerows(bucket_info_list)
