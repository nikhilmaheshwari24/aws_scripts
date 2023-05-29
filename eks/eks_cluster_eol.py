import boto3
import os
import sys
import pandas as pd

# Setting up the AWS Environment
# env = str(sys.argv[1])
# os.environ['AWS_PROFILE'] = env

regions = ['us-east-1', 'ap-southeast-1', 'ap-south-1']

session = boto3.Session()
profiles = session.available_profiles

eks_list = []

eks_eol = {'1.20': 'November 1, 2022', '1.21': 'February 15, 2023', '1.22': 'June 4, 2023', '1.23': 'October 11, 2023', '1.24': 'January 2024', '1.25': 'May 2024', '1.26': 'June 2024', '1.27': 'July 2024'}

for profile in profiles:

    for region in regions:

        profile_session = boto3.session.Session(profile_name=profile)

        acc_info = profile_session.client('sts')
        acc_sts = acc_info.get_caller_identity()

        acc_no = acc_sts['Account']
        
        eks = profile_session.client('eks', region_name = region)
        paginator = eks.get_paginator('list_clusters')
        eks_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
        

        for page in eks_paginator:
            
            for cluster in page['clusters']:

                print(acc_no,region,cluster)

                eks_cluster = eks.describe_cluster(name = cluster)
                
                eks_dict = {}                
                eks_dict['Accounts'] = acc_no
                eks_dict['Region'] = region
                eks_dict['Name'] = eks_cluster['cluster']['name']
                eks_dict['Version'] = eks_cluster['cluster']['version']
                eks_version = eks_cluster['cluster']['version']
                if eks_cluster['cluster']['version'] in eks_eol.keys():
                    eks_dict['EOL'] = eks_eol[eks_version]

                eks_list.append(eks_dict)

df = pd.DataFrame(eks_list)
filename="EKS.csv"
df.to_csv(filename)
            

            