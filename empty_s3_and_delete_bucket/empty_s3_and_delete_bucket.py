import boto3
import os
import sys

s3=boto3.resource("s3")

# Taking the All Buckets as String
all_buckets=str(sys.argv[1])

# Converting All Buckets String to Bucket List
buckets=list(map(str.strip,all_buckets.split('\n')))
print("List of Buckets:",buckets)

# Iteration on Bucket List
for bucket in buckets:
    s3_bucket=s3.Bucket(bucket)
    # Versioning check 
    bucket_versioning=s3.BucketVersioning(bucket)
    if bucket_versioning.status == 'Enabled':
        print("Versioning Enabled for Bucket and all objects will be deleted:",bucket)
        s3_bucket.object_versions.delete()
    else:
        print("Versioning Disabled for Bucket and all objects will be deleted:",bucket)
        s3_bucket.objects.all().delete()
    # Bucket delete
    s3_bucket.delete()
    print("Bucket is Deleted\n")