import boto3
import os
import csv
import sys
import pandas as pd

env=str(sys.argv[1])
os.environ['AWS_PROFILE'] = env

regions = ['us-east-1','ap-southeast-1','ap-south-1']

ec2=boto3.client('ec2',region_name=region)
sg_id = ['']

sg=ec2.describe_security_groups(GroupIds=sg_id)

rulelist=[]

for sg in sg['SecurityGroups']:
    # print (sg['IpPermissions'])
    for ipPermission in sg['IpPermissions']:
        # print (ipPermission)
        # print ('\n')
        for permission in ipPermission['IpRanges']:
            # print(permission)
            ruledict={}
            if permission.get('Description') and ipPermission.get('FromPort'):
                ruledict['GroupId']=sg['GroupId']
                ruledict['Port']=ipPermission['FromPort']
                ruledict['Protocol']=ipPermission['IpProtocol']
                ruledict['CIDR']=permission['CidrIp']
                ruledict['Description']=permission['Description']
                # print (sg['GroupId'],ipPermission['FromPort'], ipPermission['IpProtocol'], permission['CidrIp'],permission['Description'])
            elif ipPermission.get('FromPort') == '-1' or ipPermission.get('IpProtocol') == '-1':
                ruledict['GroupId']=sg['GroupId']
                ruledict['Port']='ALL'
                ruledict['Protocol']='ALL'
                ruledict['CIDR']=permission['CidrIp']
                ruledict['Description']=permission['Description']
            else :
                ruledict['GroupId']=sg['GroupId']
                ruledict['Port']=ipPermission['FromPort']
                ruledict['Protocol']=ipPermission['IpProtocol']
                ruledict['CIDR']=permission['CidrIp']
                ruledict['Description']="--"
                # print (sg['GroupId'],ipPermission['FromPort'], ipPermission['IpProtocol'], permission['CidrIp'],'--')
            rulelist.append(ruledict)

df = pd.DataFrame(rulelist)
print(df)
filename="sg-inbound-rules.csv"
df.to_csv(filename)