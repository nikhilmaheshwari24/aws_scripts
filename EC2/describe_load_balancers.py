import boto3
import os
import pandas as pd
from datetime import datetime, timezone

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define AWS regions to search for ELBs
regions = ['us-east-2']

# Initialize a list to store ELB information
elbs_list = []

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

# Function to get request metrics for ELBs
def get_request_metrics(elb_name, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/ELB',
        MetricName='RequestCount',
        Dimensions=[
            {'Name': 'LoadBalancerName', 'Value': elb_name},
        ],
        StartTime=start_time_str,
        EndTime=end_time_str,
        Period=86400,
        Statistics=['Sum'],
        Unit='Count'
    )
    if 'Datapoints' in response:
        datapoints = response['Datapoints']
        if datapoints:
            return int(datapoints[0]['Sum'])
    return None

# Iterate over each region
for region in regions:
    # Create an ELB client for the region
    elb_client = boto3.client('elb', region_name=region)
    # Describe ELBs
    paginator = elb_client.get_paginator('describe_load_balancers')
    elb_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})
    # Iterate over each page of ELBs
    for page in elb_paginator:
        # Iterate over each ELB
        for elb in page['LoadBalancerDescriptions']:
            elb_dict = {}
            # Extract ELB details
            elb_dict['LoadBalancerName'] = elb['LoadBalancerName']
            elb_dict['DNSName'] = elb['DNSName']
            elb_dict['CanonicalHostedZoneName'] = elb['CanonicalHostedZoneName']
            elb_dict['CanonicalHostedZoneNameID'] = elb['CanonicalHostedZoneNameID']
            elb_dict['ListenerDescriptions'] = '\n'.join(map(str, elb.get('ListenerDescriptions', [])))
            elb_dict['Policies_AppCookieStickinessPolicies'] = elb.get('Policies', {}).get('AppCookieStickinessPolicies', [])
            elb_dict['Policies_LBCookieStickinessPolicies'] = elb.get('Policies', {}).get('LBCookieStickinessPolicies', [])
            elb_dict['Policies_OtherPolicies'] = elb.get('Policies', {}).get('OtherPolicies', [])
            elb_dict['BackendServerDescriptions'] = '\n'.join(map(str, elb.get('BackendServerDescriptions', [])))
            elb_dict['AvailabilityZones'] = elb['AvailabilityZones']
            elb_dict['Subnets'] = elb['Subnets']
            elb_dict['VPCId'] = elb['VPCId']
            elb_dict['Instances'] = elb.get('Instances', [])
            elb_dict['SourceSecurityGroup'] = elb['SourceSecurityGroup']['GroupName']
            elb_dict['SecurityGroups'] = elb['SecurityGroups']
            elb_dict['CreatedTime'] = elb['CreatedTime']
            elb_dict['Age'] = calculate_age(elb['CreatedTime'])
            elb_dict['Scheme'] = elb['Scheme']
            # Extract ELB attributes
            elb_attributes = elb_client.describe_load_balancer_attributes(LoadBalancerName=elb['LoadBalancerName'])['LoadBalancerAttributes']
            elb_dict['Attribute_CrossZoneLoadBalancing'] = elb_attributes['CrossZoneLoadBalancing']
            elb_dict['Attribute_AccessLog'] = elb_attributes['AccessLog']
            elb_dict['Attribute_ConnectionDraining'] = elb_attributes['ConnectionDraining']
            elb_dict['Attribute_ConnectionSettings'] = elb_attributes['ConnectionSettings']
            elb_dict['Attribute_AdditionalAttributes'] = f"{elb_attributes['AdditionalAttributes'][0]['Key']}: {elb_attributes['AdditionalAttributes'][0]['Value']}"
            # Extract ELB tags
            elb_dict['Tags'] = resource_tags(elb_client.describe_tags(LoadBalancerNames=[elb['LoadBalancerName']])['TagDescriptions'][0].get('Tags', []))
            # Append ELB details to the list
            elbs_list.append(elb_dict)
            # Print ELB Name
            print(elb['LoadBalancerName'])

# Create DataFrame
df = pd.DataFrame(elbs_list)

# Write DataFrame to CSV file
filename = 'describe_load_balancers.csv'
df.to_csv(os.path.join(directory, filename), index=False)
