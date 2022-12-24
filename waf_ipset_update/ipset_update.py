import boto3
import os
import sys

#Update AWS Region
region=""
client=boto3.client("wafv2",region_name=region)

ipset_name=str(sys.argv[3])
scope=str(sys.argv[4])
ipset_id=str(sys.argv[5])

#Taking the IP Address as string
ipstr=str(sys.argv[1])
#Converting IPs string to IP list
ips=list(map(str.strip, ipstr.split(',')))
print("IP Address:",ips)

result=client.get_ip_set(Name=ipset_name,Scope=scope,Id=ipset_id)
lock_token=str(result['LockToken'])
print("LockToken is:",lock_token)
#Describing IPSet
ipset=result['IPSet']
print("IPSet details:\n",ipset)

#Extracting IP Current Addresses present in IPSet
addresses=ipset['Addresses']
print("Current Address:",addresses)

#Function
function=str(sys.argv[2])
for ip in ips:
    #Extracting the LockToken
    result=client.get_ip_set(Name=ipset_name,Scope=scope,Id=ipset_id)
    lock_token=str(result['LockToken'])
    print("LockToken is:",lock_token)
    # ipset=result['IPSet']
    # print("IPSet details:\n",ipset)

    #Extracting IP Current Addresses
    # addresses=ipset['Addresses']
    # print("Current Address:",addresses)

    # IP Address add fucntion
    if function == "add" :
        addresses.append(ip)
        print ("Adding - Updated Address List ", addresses)
        response=client.update_ip_set(Name=ipset_name,Scope=scope,Id=ipset_id,Addresses=addresses,LockToken=lock_token)
        #AWS HTTP Response
        responseMetadata=response['ResponseMetadata']
        if [ responseMetadata == 200 ]:
            print('IP Added Successfully.')
        else:
            print ("Some Issue while adding IP Addess")
        # print("add")
    # IP Address remove fucntion
    elif function == "remove" :
        index=addresses.index(ip)
        addresses.pop(index)
        print ("Removing - Updated Address List: ", addresses)
        response=client.update_ip_set(Name=ipset_name,Scope=scope,Id=ipset_id,Addresses=addresses,LockToken=lock_token)
        #AWS HTTP Response
        responseMetadata=response['ResponseMetadata']
        if [ responseMetadata == 200 ]:
            print('IP Removed Successfully.')
        else:
            print ("Some Issue while removing IP Addess")
        # print("remove")

# Bash Command to Execute.
# python3 ipset_update.py "$IP_Address" "$Function" "$IpSet_Name" "$Scope" "$Id"