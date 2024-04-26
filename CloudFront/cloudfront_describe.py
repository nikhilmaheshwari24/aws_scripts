import boto3
import os
import sys
import pandas as pd

# Setting up the AWS Environment
# env = str(sys.argv[1])
# os.environ['AWS_PROFILE'] = env

session = boto3.Session()
profiles = session.available_profiles

cloudfront_list = []

for profile in profiles:

    profile_session = boto3.session.Session(profile_name=profile)

    acc_info = profile_session.client('sts')
    acc_sts = acc_info.get_caller_identity()

    acc_no = acc_sts['Account']
    
    cloudfront = profile_session.client('cloudfront')
    paginator = cloudfront.get_paginator('list_distributions')
    cloudfront_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})
    
    # print (elasticache_paginator)

    for page in cloudfront_paginator:
        
        print(page)

        if "Items" in page['DistributionList'].keys():

            for distribution in page['DistributionList']['Items']:

                cloudfront_dict = {}
                cloudfront_dict['Accounts'] = acc_no
                cloudfront_dict['Id'] = distribution['Id']
                cloudfront_dict['Status'] = distribution['Status']
                cloudfront_dict['DomainName'] = distribution['DomainName']

                # print (acc_no,distribution['Id'],distribution['DomainName'])
            
                cloudfront_list.append(cloudfront_dict)

    print ('--\n\--')

df = pd.DataFrame(cloudfront_list)
filename="CloudFront.csv"
df.to_csv(filename)