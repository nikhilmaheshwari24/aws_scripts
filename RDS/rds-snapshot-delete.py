import csv
import boto3
import sys
import os

# csv file name
filename=".csv"

# initializing the titles and rows list
fields=[]
rows=[]

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
     
    # extracting field names through first row
    fields = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        rows.append (row)

#snapshot lists
snapshots_delete_it_north_virginia=[]
snapshots_delete_it_singapore=[]
snapshots_delete_it_mumbai=[]

# extracting snapshots for deletion
for row in rows:
    if row[9] == '' and row[3] == "us-east-1":
        snapshots_delete_it_north_virginia.append(row[0])
    elif row[9] == '' and row[3] == "ap-southeast-1":
        snapshots_delete_it_singapore.append(row[0])
    elif row[9] == '' and row[3] == "ap-south-1":
        snapshots_delete_it_mumbai.append(row[0])

print ("NorthVirginia Snapshot\n", snapshots_delete_it_north_virginia)
print ("Singapore Snapshot\n", snapshots_delete_it_singapore)
print ("Mumbai Snapshot\n", snapshots_delete_it_mumbai)


# AWS Profiling
env=str(sys.argv[1])
os.environ['AWS_PROFILE'] = env


regions = ['us-east-1', 'ap-south-1', 'ap-southeast-1']
for region in regions:
    client=boto3.client('rds',region_name=region)

    if region == "us-east-1":
        for snapshot in snapshots_delete_it_north_virginia:
            try:
                delete_snapshot=client.delete_db_snapshot(DBSnapshotIdentifier=snapshot)
                print (delete_snapshot)
            except Exception as err:
                print (snapshot,"-->",err)
            try:
                delete_cluster_snapshot=client.delete_db_cluster_snapshot(DBClusterSnapshotIdentifier=snapshot)
                print(delete_cluster_snapshot)
            except Exception as err:
                print (snapshot,"-->",err)
        print('\n')

    if region == "ap-southeast-1":
        for snapshot in snapshots_delete_it_singapore:
            try:
                delete_snapshot=client.delete_db_snapshot(DBSnapshotIdentifier=snapshot)
                print (delete_snapshot)
            except Exception as err:
                print (snapshot,"-->",err)
            try:
                delete_cluster_snapshot=client.delete_db_cluster_snapshot(DBClusterSnapshotIdentifier=snapshot)
                print(delete_cluster_snapshot)
            except Exception as err:
                print (snapshot,"-->",err)
        print('\n')

    if region == "ap-south-1":
        for snapshot in snapshots_delete_it_mumbai:
            try:
                delete_snapshot=client.delete_db_snapshot(DBSnapshotIdentifier=snapshot)
                print (delete_snapshot)
            except Exception as err:
                print (snapshot,"-->",err)
            try:
                delete_cluster_snapshot=client.delete_db_cluster_snapshot(DBClusterSnapshotIdentifier=snapshot)
                print(delete_cluster_snapshot)
            except Exception as err:
                print (snapshot,"-->",err)
        print('\n')