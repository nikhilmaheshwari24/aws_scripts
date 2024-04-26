import boto3
import os
import sys
import csv

# AWS Profiling
env=str(sys.argv[1])
os.environ['AWS_PROFILE'] = env

regions = ['us-east-1', 'ap-south-1', 'ap-southeast-1']
print ("Region,LBName,Type,S3BucketName")
for region in regions:
    # print ('\n',region)
    # print ("Classic Load Balaners: ")
    
    client=boto3.client('elb', region_name= region)
    result=client.describe_load_balancers()
    lb_list=result['LoadBalancerDescriptions']

    for lb in lb_list:
        lb_name=lb['LoadBalancerName']
        # print ("LBName:",lb_name)
        lb_attributes=client.describe_load_balancer_attributes(LoadBalancerName=lb_name)
        if lb_attributes['LoadBalancerAttributes']['AccessLog']['Enabled'] == True:
            # print ("S3BucketName:",lb_attributes['LoadBalancerAttributes']['AccessLog']['S3BucketName'])
            print(region,lb_name,'classic',lb_attributes['LoadBalancerAttributes']['AccessLog']['S3BucketName'],sep=",")
        else:
            # print ('S3BucketName: -')
            print(region,lb_name,"-",sep="")
    # print ("Application & Network Load Balaners: ")
    client=boto3.client('elbv2', region_name=region)
    result=client.describe_load_balancers()
    lb_list=result['LoadBalancers']

    for lb in lb_list:
        # print(lb)
        lb_name=lb['LoadBalancerName']
        # print(lb_name)
        lb_attributes=client.describe_load_balancer_attributes(LoadBalancerArn=lb['LoadBalancerArn'])
        # print (lb_attributes)
        if lb['Type'] == "application":
            if lb_attributes['Attributes'][0]['Value'] == 'true':
                # print ("S3BucketName:",lb_attributes['Attributes'][1]['Value'])
                print(region,lb_name,lb['Type'],lb_attributes['Attributes'][1]['Value'],sep=",")
            else:
                # print ('S3BucketName: -')
                print(region,lb_name,lb['Type'],'-',sep=",")
        elif lb['Type'] == "network":
            if lb_attributes['Attributes'][3]['Value'] == 'true':
                # print ("S3BucketName:",lb_attributes['Attributes'][4]['Value'])
                print(region,lb_name,lb['Type'],lb_attributes['Attributes'][4]['Value'],sep=",")
            else:
                # print ('S3BucketName: -')
                print(region,lb_name,lb['Type'],'-',sep=",")
