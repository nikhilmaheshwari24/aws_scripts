import boto3
import os
import sys
import csv
import pandas as pd

regions = ['us-east-1','ap-southeast-1','ap-south-1']

session = boto3.Session()
profiles = session.available_profiles

asg_with_lc_list=[]

for profile in profiles:

    for region in regions:

        profile_session = boto3.session.Session(profile_name=profile)

        acc_info = profile_session.client('sts')
        acc_sts = acc_info.get_caller_identity()

        acc_no = acc_sts['Account']

        asg = profile_session.client('autoscaling', region_name=region)
        paginator = asg.get_paginator('describe_auto_scaling_groups')
        asg_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

        for page in asg_paginator:
            
            for asg in page['AutoScalingGroups']:
                
                asg_with_lc_dict={}
                if 'LaunchConfigurationName' in asg:
                    print(acc_no, region, asg['AutoScalingGroupName'],'-----',asg['LaunchConfigurationName'])
                    asg_with_lc_dict['Account'] = acc_no
                    asg_with_lc_dict['Region'] = region
                    asg_with_lc_dict['AutoScalingGroupName'] = asg['AutoScalingGroupName']
                    asg_with_lc_dict['LaunchConfigurationName'] = asg['LaunchConfigurationName']
                    asg_with_lc_dict['MinSize'] = asg['MinSize']
                    asg_with_lc_dict['MaxSize'] = asg['MaxSize']
                    asg_with_lc_dict['DesiredCapacity'] = asg['DesiredCapacity']
                    asg_with_lc_dict['Tags'] = asg['Tags']
                else:
                    break
                
                asg_with_lc_list.append(asg_with_lc_dict)
                
df = pd.DataFrame(asg_with_lc_list)
print(df)
filename = 'asg_using_lc' + '.csv'
df.to_csv(filename)