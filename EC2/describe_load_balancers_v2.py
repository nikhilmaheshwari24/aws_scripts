import boto3
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = '683738265913_admin_exp_permission_set'

# Define AWS regions to search for ELBv2 load balancers
regions = ['us-east-2']

# Initialize a list to store ELBv2 load balancer information
elbsv2_list = []

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

# Function to extract ELBv2 load balancer attributes
def get_attributes(resource_attributes):
    # Initialize an empty list to store attributes
    attribute_list = []
    # Process each attribute and store it in the list
    for attribute in resource_attributes['Attributes']:
        key = attribute['Key']
        value = attribute['Value']
        attribute_list.append(f"{key}: {value}")
    # Return the concatenated attributes if present
    if attribute_list:
        return '\n'.join(attribute_list)
    else:
        return "No Attributes Available"
 
# Function to get request metrics for ELBsv2 ALB
def get_request_metrics(elbv2_name, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/ApplicationELB',
        MetricName='RequestCount',
        Dimensions=[
            {'Name': 'LoadBalancer', 'Value': elbv2_name},
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

# Function to get active_flow_count metrics for ELBsv2 NLB
def get_active_flow_count_metrics(elbv2_name, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/NetworkELB',
        MetricName='ActiveFlowCount',
        Dimensions=[
            {'Name': 'LoadBalancer', 'Value': elbv2_name},
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
    # Create an ELBv2 client for the region
    elbv2_client = boto3.client('elbv2', region_name=region)
    # Describe ELBv2 load balancers
    paginator = elbv2_client.get_paginator('describe_load_balancers')
    elbv2_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})
    # Iterate over each page of ELBv2 load balancers
    for page in elbv2_paginator:
        # Iterate over each ELBv2 load balancer
        for elbv2 in page['LoadBalancers']:
            elb_dict = {}
            # Extract ELBv2 load balancer details
            elb_dict['LoadBalancerArn'] = elbv2['LoadBalancerArn']
            elb_dict['DNSName'] = elbv2['DNSName']
            elb_dict['CanonicalHostedZoneId'] = elbv2['CanonicalHostedZoneId']
            elb_dict['CreatedTime'] = elbv2['CreatedTime']
            elb_dict['Age'] = calculate_age(elbv2['CreatedTime'])
            elb_dict['LoadBalancerName'] = elbv2['LoadBalancerName']
            elb_dict['Scheme'] = elbv2['Scheme']
            elb_dict['VpcId'] = elbv2['VpcId']
            elb_dict['State_Code'] = elbv2['State']['Code']
            elb_dict['State_Reason'] = elbv2['State'].get('Reason', None)
            elb_dict['Type'] = elbv2['Type']
            elb_dict['AvailabilityZones'] = '\n'.join(map(str, elbv2['AvailabilityZones']))
            elb_dict['SecurityGroups'] = elbv2.get('SecurityGroups', [])
            elb_dict['IpAddressType'] = elbv2['IpAddressType']
            elb_dict['CustomerOwnedIpv4Pool'] = elbv2.get('CustomerOwnedIpv4Pool', None)
            elb_dict['EnforceSecurityGroupInboundRulesOnPrivateLinkTraffic'] = elbv2.get('EnforceSecurityGroupInboundRulesOnPrivateLinkTraffic', None)
            # Extract ELBv2 load balancer attributes
            elbv2_attributes = get_attributes(elbv2_client.describe_load_balancer_attributes(LoadBalancerArn=str(elbv2['LoadBalancerArn'])))
            elb_dict['ELBv2_Attributes'] = elbv2_attributes
            # Extract ELBv2 load balancer tags
            elb_dict['Tags'] = resource_tags(elbv2_client.describe_tags(ResourceArns=[str(elbv2['LoadBalancerArn'])])['TagDescriptions'][0].get('Tags', []))
            # Extract ELBv2 Active Flow Count (NLB) & Request Count (ALB) metrics
            if elbv2['Type'] == 'network':
                elb_dict['NLB: ActiveFLowCount / ALB: RequestCount'] = get_active_flow_count_metrics(elbv2['LoadBalancerArn'].rsplit("loadbalancer/", 1)[-1],region)
            else:
                elb_dict['NLB: ActiveFLowCount / ALB: RequestCount'] = get_request_metrics(elbv2['LoadBalancerArn'].rsplit("loadbalancer/", 1)[-1],region)

            # Append ELBv2 load balancer details to the list
            elbsv2_list.append(elb_dict)

            # Print ELBv2 Name
            print(elbv2['LoadBalancerArn'].rsplit("loadbalancer/", 1)[-1], " <> " ,elb_dict['Type'], " <> " ,elb_dict['NLB: ActiveFLowCount / ALB: RequestCount'])

# Create DataFrame
df = pd.DataFrame(elbsv2_list)

# Write DataFrame to CSV file
filename = 'describe_load_balancers_v2.csv'
df.to_csv(os.path.join(directory, filename), index=False)