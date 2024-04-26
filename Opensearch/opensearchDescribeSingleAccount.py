import os
import sys
import boto3
import pandas as pd

# Command python3.11 opensearchDescribeSingleAccount.py <profile_name>

# Setting the environment
env = str(sys.argv[1])  # Fetches profile name from command-line argument
os.environ['AWS_PROFILE'] = env  # Sets AWS profile

regions = ['us-east-2']  # Define AWS regions of interest

opensearch_list = []  # Initialize an empty list to store OpenSearch domain details

for region in regions:
    # OpenSearch client initialization
    opensearch = boto3.client('opensearch', region_name=region)
    
    # Retrieve all OpenSearch domains in the specified region
    opensearch_domains = opensearch.list_domain_names()['DomainNames']

    # Iterate through each OpenSearch domain
    for domain in opensearch_domains:
        opensearch_dict = {}  # Initialize a dictionary for domain details
        
        # Retrieve details of the OpenSearch domain
        domain_details = opensearch.describe_domain(DomainName=domain['DomainName'])['DomainStatus']

        # Store various domain attributes with existence checks
        opensearch_dict['DomainName'] = domain_details.get('DomainName')
        opensearch_dict['EngineVersion'] = domain_details.get('EngineVersion')
        opensearch_dict['DataNode InstanceType'] = domain_details['ClusterConfig'].get('InstanceType')
        opensearch_dict['DataNode InstanceCount'] = domain_details['ClusterConfig'].get('InstanceCount')

        # Check and retrieve DedicatedMaster related details if available
        opensearch_dict['DedicatedMasterEnabled'] = domain_details['ClusterConfig'].get('DedicatedMasterEnabled', False)
        opensearch_dict['MasterNode InstanceType'] = domain_details['ClusterConfig'].get('DedicatedMasterType', "None")
        opensearch_dict['MasterNode InstanceCount'] = domain_details['ClusterConfig'].get('DedicatedMasterCount', "None")

        # Retrieve EBS options and other domain-related attributes
        opensearch_dict['VolumeType'] = domain_details['EBSOptions'].get('VolumeType')
        opensearch_dict['VolumeSize'] = domain_details['EBSOptions'].get('VolumeSize')
        opensearch_dict['Iops'] = domain_details['EBSOptions'].get('Iops')
        opensearch_dict['Throughput'] = domain_details['EBSOptions'].get('Throughput')
        opensearch_dict['VPCId'] = domain_details['VPCOptions'].get('VPCId')
        opensearch_dict['SubnetIds'] = domain_details['VPCOptions'].get('SubnetIds')
        opensearch_dict['SecurityGroupIds'] = domain_details['VPCOptions'].get('SecurityGroupIds')
        opensearch_dict['AvailabilityZones'] = domain_details['VPCOptions'].get('AvailabilityZones')
        opensearch_dict['CurrentVersion'] = domain_details['ServiceSoftwareOptions'].get('CurrentVersion')
        opensearch_dict['NewVersion'] = domain_details['ServiceSoftwareOptions'].get('NewVersion')
        opensearch_dict['UpdateAvailable'] = domain_details['ServiceSoftwareOptions'].get('UpdateAvailable')

        # Append domain details to the list
        opensearch_list.append(opensearch_dict)

# Convert the list of domain details into a Pandas DataFrame
df = pd.DataFrame(opensearch_list)

# Save DataFrame to a CSV file
filename = "opensearch.csv"
df.to_csv(filename)