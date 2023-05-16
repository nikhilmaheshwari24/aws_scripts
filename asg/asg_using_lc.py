import boto3
import pandas as pd

# List of regions to iterate over
regions = ['us-east-1', 'ap-southeast-1', 'ap-south-1']

# Create a session using default credentials
session = boto3.Session()

# Get available profiles from the session
profiles = session.available_profiles

# List to store Auto Scaling Groups with Launch Configurations
asg_with_lc_list = []

# Iterate over each profile
for profile in profiles:
    # Iterate over each region
    for region in regions:
        # Create a session with the current profile
        profile_session = boto3.session.Session(profile_name=profile)

        # Get the account information for the profile
        acc_info = profile_session.client('sts')
        acc_sts = acc_info.get_caller_identity()
        acc_no = acc_sts['Account']

        # Create an Auto Scaling client for the region
        asg = profile_session.client('autoscaling', region_name=region)

        # Use a paginator to retrieve Auto Scaling Groups
        paginator = asg.get_paginator('describe_auto_scaling_groups')
        asg_paginator = paginator.paginate(PaginationConfig={'PageSize': 50})

        # Iterate over each page of Auto Scaling Groups
        for page in asg_paginator:
            # Iterate over each Auto Scaling Group
            for asg in page['AutoScalingGroups']:
                asg_with_lc_dict = {}
                if 'LaunchConfigurationName' in asg:
                    # Print and store information for Auto Scaling Groups with Launch Configurations
                    print(acc_no, region, asg['AutoScalingGroupName'], '-----', asg['LaunchConfigurationName'])
                    asg_with_lc_dict['Account'] = acc_no
                    asg_with_lc_dict['Region'] = region
                    asg_with_lc_dict['AutoScalingGroupName'] = asg['AutoScalingGroupName']
                    asg_with_lc_dict['LaunchConfigurationName'] = asg['LaunchConfigurationName']
                    asg_with_lc_dict['MinSize'] = asg['MinSize']
                    asg_with_lc_dict['MaxSize'] = asg['MaxSize']
                    asg_with_lc_dict['DesiredCapacity'] = asg['DesiredCapacity']
                    asg_with_lc_dict['Tags'] = asg['Tags']
                else:
                    # Skip Auto Scaling Groups without Launch Configurations
                    break

                # Append the dictionary to the list
                asg_with_lc_list.append(asg_with_lc_dict)

# Create a DataFrame from the list
df = pd.DataFrame(asg_with_lc_list)

# Print the DataFrame
print(df)

# Export the DataFrame to a CSV file
filename = 'asg_using_lc.csv'
df.to_csv(filename)
