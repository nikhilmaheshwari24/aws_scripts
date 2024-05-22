import boto3
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import time

# Set AWS profile environment variable
os.environ["AWS_PROFILE"] = "683738265913_admin_exp_permission_set"

# Converts datetime to ISO 8601 format
def format_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# Converts timedelta to days
def format_timedelta(td):
    return td.days

# Calculate the age of the key in days
def calculate_key_age(create_date):
    return format_timedelta(datetime.now(timezone.utc) - create_date)

# Initialize the IAM client
iam_client = boto3.client('iam')

# # Initialize the CloudTrail client
# cloudtrail_client = boto3.client('cloudtrail')

# # Initialize the CloudWatch client for CloudTrail logs
# logs_client = boto3.client('logs')

# Fetch all IAM users
users = iam_client.list_users()['Users']

# Initialize an empty list to store user information
user_list = []

# Loop through each user to gather details
for user in users:

    user_dict = {}
    # Fetch user details
    user_dict['Username'] = user.get('UserName', '')
    user_dict['Path'] = user.get('Path', '')
    user_dict['ARN'] = user.get('Arn', '')
    user_dict['Creation Time'] = format_datetime(user.get('CreateDate', ''))
    
    # Fetch user groups details
    try:
        user_groups = iam_client.list_groups_for_user(UserName=user_dict['Username'])['Groups']
        user_dict['Group'] = ', '.join(group['GroupName'] for group in user_groups)
    except Exception:
        user_dict['Group'] = ''

    # # Fetch last activity (CloudTrail events)
    # try:
    #     end_time = datetime.now(timezone.utc)
    #     start_time = end_time - timedelta(days=90)  # Last 90 days

    #     response = cloudtrail_client.lookup_events(
    #         LookupAttributes=[{'AttributeKey': 'Username', 'AttributeValue': user_dict['Username']}],
    #         StartTime=start_time,
    #         EndTime=end_time,
    #         MaxResults=1
    #     )

    #     events = response.get('Events', [])
    #     if events:
    #         last_activity = events[0]['EventTime']
    #         user_dict['Last Activity'] = format_datetime(last_activity)
    #     else:
    #         user_dict['Last Activity'] = ''
    # except Exception:
    #     user_dict['Last Activity'] = ''

    # Fetch MFA details
    try:
        mfa_devices = iam_client.list_mfa_devices(UserName=user_dict['Username'])['MFADevices']
        user_dict['MFA'] = 'Enabled' if mfa_devices else 'Disabled'
    except Exception:
        user_dict['MFA'] = ''

    # Fetch password age and console access details
    try:
        login_profile = iam_client.get_login_profile(UserName=user_dict['Username'])
        password_last_used = user.get('PasswordLastUsed', None)
        if password_last_used:
            user_dict['Password Age'] = format_timedelta(datetime.now(timezone.utc) - password_last_used)
        else:
            user_dict['Password Age'] = ''
        user_dict['Console Access'] = 'Enabled'
        user_dict['Console last sign-in'] = format_datetime(password_last_used) if password_last_used else ''
    except Exception:
        user_dict['Password Age'] = ''
        user_dict['Console Access'] = 'Disabled'
        user_dict['Console last sign-in'] = ''

    # Initialize access key details
    user_dict['Access_Keys_1'] = ''
    user_dict['Access_Keys_1_Description'] = ''
    user_dict['Access_Keys_1_Last_Used'] = ''
    user_dict['Access_Keys_1_Last_Region'] = ''
    user_dict['Access_Keys_1_Last_Service'] = ''
    user_dict['Access_Keys_1_Created'] = ''
    user_dict['Access_Keys_1_Status'] = ''
    user_dict['Access_Key_1_Age'] = ''
    user_dict['Access_Keys_2'] = ''
    user_dict['Access_Keys_2_Description'] = ''
    user_dict['Access_Keys_2_Last_Used'] = ''
    user_dict['Access_Keys_2_Last_Region'] = ''
    user_dict['Access_Keys_2_Last_Service'] = ''
    user_dict['Access_Keys_2_Created'] = ''
    user_dict['Access_Keys_2_Status'] = ''
    user_dict['Access_Key_2_Age'] = ''

    # Fetch access key details
    try:
        access_keys = iam_client.list_access_keys(UserName=user_dict['Username'])['AccessKeyMetadata']
        if len(access_keys) >= 1:
            key_1 = access_keys[0]
            user_dict['Access_Keys_1'] = key_1['AccessKeyId']
            user_dict['Access_Keys_1_Description'] = ''
            user_dict['Access_Keys_1_Last_Used'] = ''
            user_dict['Access_Keys_1_Last_Region'] = ''
            user_dict['Access_Keys_1_Last_Service'] = ''
            user_dict['Access_Keys_1_Created'] = format_datetime(key_1['CreateDate'])
            user_dict['Access_Keys_1_Status'] = key_1['Status']
            user_dict['Access_Key_1_Age'] = calculate_key_age(key_1['CreateDate'])

            # Fetch last used details for key 1
            try:
                key_1_last_used = iam_client.get_access_key_last_used(AccessKeyId=key_1['AccessKeyId'])['AccessKeyLastUsed']
                user_dict['Access_Keys_1_Last_Used'] = format_datetime(key_1_last_used['LastUsedDate'])
                user_dict['Access_Keys_1_Last_Region'] = key_1_last_used.get('Region', '')
                user_dict['Access_Keys_1_Last_Service'] = key_1_last_used.get('ServiceName', '')
            except Exception:
                pass

        if len(access_keys) >= 2:
            key_2 = access_keys[1]
            user_dict['Access_Keys_2'] = key_2['AccessKeyId']
            user_dict['Access_Keys_2_Description'] = ''
            user_dict['Access_Keys_2_Last_Used'] = ''
            user_dict['Access_Keys_2_Last_Region'] = ''
            user_dict['Access_Keys_2_Last_Service'] = ''
            user_dict['Access_Keys_2_Created'] = format_datetime(key_2['CreateDate'])
            user_dict['Access_Keys_2_Status'] = key_2['Status']
            user_dict['Access_Key_2_Age'] = calculate_key_age(key_2['CreateDate'])

            # Fetch last used details for key 2
            try:
                key_2_last_used = iam_client.get_access_key_last_used(AccessKeyId=key_2['AccessKeyId'])['AccessKeyLastUsed']
                user_dict['Access_Keys_2_Last_Used'] = format_datetime(key_2_last_used['LastUsedDate'])
                user_dict['Access_Keys_2_Last_Region'] = key_2_last_used.get('Region', '')
                user_dict['Access_Keys_2_Last_Service'] = key_2_last_used.get('ServiceName', '')
            except Exception:
                pass
        else:
            user_dict['Access_Keys_2'] = ''
            user_dict['Access_Keys_2_Description'] = ''
            user_dict['Access_Keys_2_Last_Used'] = ''
            user_dict['Access_Keys_2_Last_Region'] = ''
            user_dict['Access_Keys_2_Last_Service'] = ''
            user_dict['Access_Keys_2_Created'] = ''
            user_dict['Access_Keys_2_Status'] = ''
            user_dict['Access_Key_2_Age'] = ''
    except Exception:
        user_dict['Access_Keys_1'] = ''
        user_dict['Access_Keys_1_Description'] = ''
        user_dict['Access_Keys_1_Last_Used'] = ''
        user_dict['Access_Keys_1_Last_Region'] = ''
        user_dict['Access_Keys_1_Last_Service'] = ''
        user_dict['Access_Keys_1_Created'] = ''
        user_dict['Access_Keys_1_Status'] = ''
        user_dict['Access_Key_1_Age'] = ''
        user_dict['Access_Keys_2'] = ''
        user_dict['Access_Keys_2_Description'] = ''
        user_dict['Access_Keys_2_Last_Used'] = ''
        user_dict['Access_Keys_2_Last_Region'] = ''
        user_dict['Access_Keys_2_Last_Service'] = ''
        user_dict['Access_Keys_2_Created'] = ''
        user_dict['Access_Keys_2_Status'] = ''
        user_dict['Access_Key_2_Age'] = ''

    # Fetch signing certificates
    try:
        signing_certs = iam_client.list_signing_certificates(UserName=user_dict['Username'])['Certificates']
        user_dict['Signing Certs'] = ', '.join(cert['CertificateId'] for cert in signing_certs)
    except Exception:
        user_dict['Signing Certs'] = ''

    # Fetch user policies attached
    try:
        user_policies = iam_client.list_attached_user_policies(UserName=user_dict['Username'])['AttachedPolicies']
        user_dict['Policys Attached Name'] = ', '.join(policy['PolicyName'] for policy in user_policies)
    except Exception:
        user_dict['Policys Attached Name'] = ''

    # Fetch user tags
    try:
        user_tags = iam_client.list_user_tags(UserName=user_dict['Username'])['Tags']
        user_dict['Tags'] = ', '.join(f"{tag['Key']}={tag['Value']}" for tag in user_tags)
    except Exception:
        user_dict['Tags'] = ''

    # SSH Public Keys for AWS CodeCommit
    ssh_public_keys = iam_client.list_ssh_public_keys(UserName=user_dict['Username']).get('SSHPublicKeys', [])
    user_dict['SSH public keys for AWS CodeCommit Details'] = ", ".join([key['SSHPublicKeyId'] for key in ssh_public_keys])

    # HTTPS Git credentials for AWS CodeCommit
    https_git_creds = iam_client.list_service_specific_credentials(UserName=user_dict['Username']).get('ServiceSpecificCredentials', [])
    user_dict['HTTPS Git credentials for AWS CodeCommit Details'] = ", ".join([cred['ServiceSpecificCredentialId'] for cred in https_git_creds if cred['ServiceName'] == 'codecommit.amazonaws.com'])

    # Credentials for Amazon Keyspaces (for Apache Cassandra)
    cassandra_creds = [cred['ServiceSpecificCredentialId'] for cred in https_git_creds if cred['ServiceName'] == 'cassandra.amazonaws.com']
    user_dict['Credentials for Amazon Keyspaces (for Apache Cassandra) Details'] = ", ".join(cassandra_creds)

    # X.509 Signing certificates
    x509_certs = iam_client.list_server_certificates().get('ServerCertificateMetadataList', [])
    user_dict['X.509 Signing certificates Details'] = ", ".join([cert['ServerCertificateId'] for cert in x509_certs])

    # Allowed services
    services_last_accessed = iam_client.generate_service_last_accessed_details(Arn=user['Arn'])
    job_id = services_last_accessed['JobId']

    # Wait for the job to complete
    while True:
        job_status = iam_client.get_service_last_accessed_details(JobId=job_id)
        if job_status['JobStatus'] == 'COMPLETED':
            break
        time.sleep(1)

    allowed_services = job_status.get('ServicesLastAccessed', [])
    allowed_services_str = ", ".join(
        [f"{service['ServiceName']} (Last Accessed: {service.get('LastAuthenticated', 'N/A')})"
         for service in allowed_services]
    )
    user_dict['Allowed services (Service, Policy, Last Accessed) Details'] = allowed_services_str

    # Add the user_dict to the list
    user_list.append(user_dict)

    print(user_dict['Username'], " <> ", user_dict['Access_Keys_1'], ",", user_dict['Access_Keys_2'])

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(user_list)

# Save the DataFrame to a CSV file
df.to_csv('iam_user_details.csv', index=False)
