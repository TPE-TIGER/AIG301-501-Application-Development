import os, time, json
from ftplib import FTP
import boto3
from botocore.exceptions import ClientError

_config = None

with open('/app/cfg/config.json') as f:
    _config = json.load(f)

ftp_ip = _config['ftp']['ip']
ftp_user = _config['ftp']['username']
ftp_pw = _config['ftp']['password']
aws_key_id = _config['aws']['key_id']
aws_key = _config['aws']['key']
s3_bucket = _config['aws']['s3_bucket']
sname = _config['file']['source']
cname = _config['file']['cache']
dname = _config['file']['destination']

print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Job started')

# Download file
with FTP(ftp_ip, ftp_user, ftp_pw) as c:
    c.retrbinary('RETR ' + sname, open(cname, 'wb').write)

# Upload to S3
s3_client = boto3.client('s3',
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_key)
try:
    response = s3_client.upload_file(cname, s3_bucket, dname)
except ClientError as e:
    print(e)

print(time.strftime('%Y/%m/%d %H:%M:%S') + ' File uploaded')
os.remove(cname)

