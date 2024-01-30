import boto3
from datetime import datetime, timedelta, timezone

def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    s3_client = boto3.client('s3')
    sns_client = boto3.client('sns')

    # Get all users in the AWS account
    response = iam_client.list_users()

    for user in response['Users']:
        username = user['UserName']

        # Get the user's access keys
        access_keys = iam_client.list_access_keys(UserName=username)['AccessKeyMetadata']

        for key in access_keys:
            key_id = key['AccessKeyId']
            last_rotated = key['CreateDate'].replace(tzinfo=timezone.utc)

            # Check if the key is older than 60 days
            if datetime.now(timezone.utc) - last_rotated > timedelta(days=60):
                # Generate new access and secret keys
                new_access_key = iam_client.create_access_key(UserName=username)['AccessKey']
                new_access_key_id = new_access_key['AccessKeyId']
                new_secret_key = new_access_key['SecretAccessKey']

                # Update user's access key
                iam_client.update_access_key(UserName=username, AccessKeyId=key_id, Status='Inactive')

                # Store secret key in S3 bucket
                bucket_name = 'rotate-accesskeys-lambda'
                key_name = f'{username}/secret_key.txt'
                s3_client.put_object(Body=new_secret_key, Bucket=bucket_name, Key=key_name)

                # Notify user via SNS
                sns_topic_arn = 'arn:aws:sns:us-east-1:889142710491:rotate-accesskeys'
                message = f'Your access and secret keys have been rotated. New secret key stored in S3 bucket: s3://{bucket_name}/{key_name}'
                sns_client.publish(TopicArn=sns_topic_arn, Message=message, Subject='Access Key Rotation')

    return {
        'statusCode': 200,
        'body': 'Access keys rotated successfully for users exceeding 60 days.'
    }
