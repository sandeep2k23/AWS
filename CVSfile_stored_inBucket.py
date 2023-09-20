import boto3
import datetime
import csv

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    total_size_bytes = 0
    total_object_count = 0
    
    bucket_details = []

    for bucket in s3_client.list_buckets()['Buckets']:
        region = s3_client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
        if region is None:
            region = 'us-east-1'
        elif region == 'EU':
            region = 'eu-west-1'

        s3_resource = boto3.resource('s3', region_name=region)
        
        total_size = 0
        object_count = 0
        
        for obj in s3_resource.Bucket(bucket['Name']).objects.all():
            total_size += obj.size
            object_count += 1
        
        total_size_bytes += total_size
        total_object_count += object_count
        
        bucket_info = {
            'BucketName': bucket['Name'],
            'Region': region,
            'Size': total_size,
            'ObjectCount': object_count
        }

        bucket_details.append(bucket_info)

    # Write the bucket details to a CSV file
    file_name = '/tmp/bucket_details.csv'  # File path in the Lambda environment
    with open(file_name, 'w', newline='') as file:
        fieldnames = ['BucketName', 'Region', 'Size', 'ObjectCount']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bucket_details)

    # Upload the file to an S3 bucket
    bucket_name = '2buckassssdww'  # Replace with your S3 bucket name
    file_key = 'bucket_details.csv'  # Replace with the desired file name/key in the bucket

    s3_client.upload_file(file_name, bucket_name, file_key)

    print(f"Bucket details file uploaded to S3 bucket: {bucket_name}, file key: {file_key}")
    print(f"Total size of all buckets: {total_size_bytes} bytes")
    print(f"Total object count in all buckets: {total_object_count}")
