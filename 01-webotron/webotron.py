import boto3
import click
import botocore.exceptions import ClientError


session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')


@click.group()
def cli():
    "Webtron deploys websites to AWS"
    pass

@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List objects in S3 bucket"
    for obj in s3.Bucket('bucket').objects.all():
        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
        "Create and Configure s3 bucket"
        s3_bucket =  None

        try:
            s3_bucket = s3.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': session.region_name} )
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket=s3.bucket(bucket)
            else:
                raise e



        policy = """
         {
           "Version":"2012-10-17",
           "Statement":[{
             "Sid":"PublicReadGetObject",
               "Effect":"Allow",
               "Principal": "*",
               "Action":["s3:GetObject"],
               "Resource":["arn:aws:s3:::%s/*"
               ]
             }
           ]
         }
        : """ % s3_bucket.name

        policy=policy.strip()

        pol = s3_bucket.policy()
        pol.put(Policy=policy)

        ws = s3_bucket.Website()

        ws.put(WebsiteConfiguration={
         'ErrorDocument': {
                     'Key': 'error.html'
                 },
                 'IndexDocument': {
                     'Suffix': 'index.html'
                }
                })

                return

if __name__ == '__main__':
    cli()
