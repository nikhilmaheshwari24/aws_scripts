import boto3
import os
import pandas as pd

# Set AWS profile environment variable
os.environ['AWS_PROFILE'] = ''

# Define a directory to store CSV files
directory = 'CSV'
if not os.path.exists(directory):
    os.makedirs(directory)

regions = ['us-east-2']

# Initialize an empty list to store instance details
nodegroup_info = []

# Iterate over each AWS region
for region in regions:

    # Create an EKS client for the specified region
    eks_client = boto3.client('eks', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    iam_client = boto3.client('iam', region_name=region)
    
    # Initialize a paginator for list_clusters operation
    paginator = eks_client.get_paginator('list_clusters')
    cluster_paginator = paginator.paginate(PaginationConfig={'PageSize': 100})
    
    # Iterate through each page of clusters
    for cluster_page in cluster_paginator:
        for cluster in cluster_page['clusters']:
            # Initialize a paginator for list_nodegroups operation
            node_paginator = eks_client.get_paginator('list_nodegroups').paginate(clusterName=cluster, PaginationConfig={'PageSize': 100})
            
            # Iterate through each page of node groups
            for node_page in node_paginator:
                for nodegroup in node_page['nodegroups']:
                    # Get details of the node group
                    nodegroup_details = eks_client.describe_nodegroup(clusterName=cluster, nodegroupName=nodegroup)['nodegroup']
                    desired_instances = nodegroup_details['scalingConfig']['desiredSize']
                    min_instances = nodegroup_details['scalingConfig']['minSize']
                    max_instances = nodegroup_details['scalingConfig']['maxSize']

                    if desired_instances > 1:
                        # Fetch EC2 instances associated with the node group
                        filters = [{'Name': 'tag:eks:nodegroup-name', 'Values': [nodegroup]}]
                        ec2_instances = ec2_client.describe_instances(Filters=filters)['Reservations']
                        
                        iam_role = None
                        iam_policies = []
                        
                        # Process only one instance to get IAM role and policies
                        if ec2_instances:
                            instance = ec2_instances[0]['Instances'][0]
                            
                            # Fetch IAM role attached to the instance
                            if 'IamInstanceProfile' in instance:
                                instance_profile_arn = instance['IamInstanceProfile']['Arn']
                                instance_profile_name = instance_profile_arn.split('/')[-1]
                                instance_profile = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
                                
                                if instance_profile['InstanceProfile']['Roles']:
                                    iam_role = instance_profile['InstanceProfile']['Roles'][0]['RoleName']
                                    
                                    # Fetch policies attached to the IAM role
                                    attached_policies = iam_client.list_attached_role_policies(RoleName=iam_role)['AttachedPolicies']
                                    for policy in attached_policies:
                                        iam_policies.append(policy['PolicyName'])
                                    
                                    # Fetch inline policies attached to the IAM role
                                    inline_policies = iam_client.list_role_policies(RoleName=iam_role)['PolicyNames']
                                    iam_policies.extend(inline_policies)
                        
                        # Append node group details to the list
                        nodegroup_info.append({
                            'Cluster Name': cluster,
                            'Nodegroup Name': nodegroup,
                            'Desired Instances': desired_instances,
                            'Min Instances': min_instances,
                            'Max Instances': max_instances,
                            'IAM Role Name': iam_role,
                            'IAM Policies': '\n'.join(iam_policies)
                        })

                        print (cluster, nodegroup, iam_role)

# Create a DataFrame using pandas
df = pd.DataFrame(nodegroup_info)

# Write the DataFrame to a CSV file
filename = 'nodegroup_info.csv'
df.to_csv(os.path.join(directory, filename), index=False)

print("Script execution completed. CSV file saved as:", filename)
