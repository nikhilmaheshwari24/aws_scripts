import boto3
import boto3.session
import pandas as pd
import csv

regions = ['ap-southeast-1', 'us-east-1', 'ap-south-1']

session = boto3.Session()
profiles = session.available_profiles
# print(profiles)

ip_list=[]

for profile in profiles: 

    for region in regions:
        
        profile_session = boto3.session.Session(profile_name=profile)
        net_interfaces = profile_session.client('ec2', region_name=region)
        paginator = net_interfaces.get_paginator('describe_network_interfaces')
        net_interfaces_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

        for page in net_interfaces_paginator:
            
            for interface in page['NetworkInterfaces']:

                publicIp_dict={}

                if 'Association' in interface.keys(): 
                    publicIp_dict['OwnerId']=interface['OwnerId']
                    publicIp_dict['Region']=region
                    publicIp_dict['NetworkInterfaceId']=interface['NetworkInterfaceId']
                    publicIp_dict['InterfaceType']=interface['InterfaceType']
                    publicIp_dict['PublicIP']=interface['Association']['PublicIp']
                    
                    print(interface['OwnerId'],interface['InterfaceType'],interface['Association']['PublicIp'],region)
                else:
                    continue

                ip_list.append(publicIp_dict)

df = pd.DataFrame(ip_list)
print(df)
filename="org_public_ips" + ".csv"
df.to_csv(filename)  