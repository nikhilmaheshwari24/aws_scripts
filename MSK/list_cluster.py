import boto3
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define AWS regions to search for Kafka clusters
regions = ['us-east-2']

# Initialize a list to store Kafka cluster information
clusters_list = []

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
    tag_list = []
    for tag in resource_tags_list:
        key = tag['Key']
        value = tag['Value']
        tag_list.append(f"{key}: {value}")
    if tag_list:
        return '\n'.join(tag_list)
    else:
        return "No Tags Available"
        
# Function to get request metrics for Kafka clusters
def get_cpu_by_brokers_metrics(cluster_name, number_of_broker_nodes, region):
    
    brokers_max_cpus = []

    for broker_id in range(1, number_of_broker_nodes + 1):
        namespace = "AWS/Kafka"
        metric_name = "CpuUser"
        dimension_name = "Cluster Name"
        broker_id_dimension = "Broker ID"
        start_time = datetime.utcnow() - timedelta(days=14)
        end_time = datetime.utcnow()
        period = 86400

        cloudwatch = boto3.client('cloudwatch', region_name=region)

        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[
                {'Name': dimension_name, 'Value': cluster_name},
                {'Name': broker_id_dimension, 'Value': str(broker_id)}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )

        max_average = max([datapoint['Average'] for datapoint in response.get('Datapoints', [])], default=0)
        brokers_max_cpus.append(max_average)

    return brokers_max_cpus

# Iterate over each region
for region in regions: 
    # Create a Kafka client for the region
    kafka_client = boto3.client('kafka',region_name=region)
    # Paginate through the list of Kafka clusters
    paginator = kafka_client.get_paginator('list_clusters')
    kafka_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})
    # Iterate over each page of Kafka clusters
    for page in kafka_paginator:
        # Iterate over each Kafka cluster
        for cluster in page['ClusterInfoList']:
            cluster_dict = {}
            # Extract Kafka cluster details
            cluster_dict['ActiveOperationArn'] = cluster.get('ActiveOperationArn', None)
            cluster_dict['BrokerNodeGroupInfo'] = cluster['BrokerNodeGroupInfo']
            cluster_dict['BrokerNodeGroupInfo'] = cluster['BrokerNodeGroupInfo']['BrokerAZDistribution']
            cluster_dict['BrokerNodeGroupInfo_ClientSubnets'] = cluster['BrokerNodeGroupInfo']['ClientSubnets']
            cluster_dict['BrokerNodeGroupInfo_InstanceType'] = cluster['BrokerNodeGroupInfo']['InstanceType']
            cluster_dict['BrokerNodeGroupInfo_SecurityGroups'] = cluster['BrokerNodeGroupInfo']['SecurityGroups']
            cluster_dict['BrokerNodeGroupInfo_StorageInfo'] = cluster['BrokerNodeGroupInfo']['StorageInfo']
            cluster_dict['BrokerNodeGroupInfo_ConnectivityInfo_PublicAccess'] = cluster['BrokerNodeGroupInfo']['ConnectivityInfo']['PublicAccess']
            cluster_dict['BrokerNodeGroupInfo_ConnectivityInfo_VpcConnectivity'] = cluster['BrokerNodeGroupInfo']['ConnectivityInfo']['VpcConnectivity']
            cluster_dict['BrokerNodeGroupInfo_ZoneIds'] = cluster['BrokerNodeGroupInfo']['ZoneIds']
            
            cluster_dict['ClientAuthentication_SASL'] = cluster['ClientAuthentication'].get('Sasl', None)
            cluster_dict['ClientAuthentication_TLS'] = cluster['ClientAuthentication'].get('Tls', None)
            cluster_dict['ClientAuthentication_Unauthenticated'] = cluster['ClientAuthentication'].get('Unauthenticated',None)

            cluster_dict['ClusterArn'] = cluster['ClusterArn']
            cluster_dict['ClusterName'] = cluster['ClusterName']
            cluster_dict['CreationTime'] = cluster['CreationTime']
            cluster_dict['Age'] = calculate_age(cluster['CreationTime'])
            cluster_dict['CurrentVersion'] = cluster['CurrentVersion']

            cluster_dict['EncryptionAtRest'] = cluster['EncryptionInfo']['EncryptionAtRest']
            cluster_dict['EncryptionInTransit'] = cluster['EncryptionInfo']['EncryptionInTransit']

            cluster_dict['EnhancedMonitoring'] = cluster['EnhancedMonitoring']

            cluster_dict['Prometheus_JmxExporter'] = cluster['OpenMonitoring']['Prometheus']['JmxExporter']['EnabledInBroker']
            cluster_dict['Prometheus_NodeExporter'] = cluster['OpenMonitoring']['Prometheus']['NodeExporter']['EnabledInBroker']

            cluster_dict['CloudWatchLogs_Enabled'] = cluster['LoggingInfo']['BrokerLogs']['CloudWatchLogs']['Enabled']
            cluster_dict['CloudWatchLogs_LogGroup'] = cluster['LoggingInfo']['BrokerLogs']['CloudWatchLogs'].get('LogGroup', None)
            cluster_dict['Firehose_Enabled'] = cluster['LoggingInfo']['BrokerLogs']['Firehose']['Enabled']
            cluster_dict['Firehose_DeliveryStream'] = cluster['LoggingInfo']['BrokerLogs']['Firehose'].get('DeliveryStream', None)
            cluster_dict['S3_Enabled'] = cluster['LoggingInfo']['BrokerLogs']['S3']['Enabled']
            cluster_dict['S3_Bucket'] = cluster['LoggingInfo']['BrokerLogs']['S3'].get('Bucket', None)
            cluster_dict['S3_Prefix'] = cluster['LoggingInfo']['BrokerLogs']['S3'].get('Prefix', None)
            cluster_dict['S3_Enabled'] = cluster['LoggingInfo']['BrokerLogs']['S3']['Enabled']
            
            cluster_dict['NumberOfBrokerNodes'] = cluster['NumberOfBrokerNodes']
            cluster_dict['State'] = cluster['State']
            cluster_dict['StateInfo_Code'] = cluster.get('StateInfo', {}).get('Code', None)
            cluster_dict['StateInfo_Message'] = cluster.get('StateInfo', {}).get('Message', None)
            cluster_dict['Tags'] = cluster['Tags']
            cluster_dict['ZookeeperConnectString'] = cluster['ZookeeperConnectString']
            cluster_dict['ZookeeperConnectStringTls'] = cluster['ZookeeperConnectStringTls']
            cluster_dict['StorageMode'] = cluster['StorageMode']
            cluster_dict['CustomerActionStatus'] = cluster['CustomerActionStatus']

            cluster_dict['CPU Usage by Broker']= get_cpu_by_brokers_metrics(cluster_dict['ClusterName'], cluster_dict['NumberOfBrokerNodes'], region)
            
            # Append Kafka cluster details to the list
            clusters_list.append(cluster_dict)
            # Print Kafka cluster name
            print(cluster['ClusterName'], " <> ", cluster_dict['CPU Usage by Broker'])
            

# Create DataFrame
df = pd.DataFrame(clusters_list)

# Write DataFrame to CSV file
filename = 'list_clusters.csv'
df.to_csv(os.path.join(directory, filename), index=False)
