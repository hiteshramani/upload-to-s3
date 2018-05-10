from flask import Flask
import boto3
from flask_sqlalchemy import SQLAlchemy

# initiating the app
app = Flask(__name__)
app.config.from_object('settings')

# initiating the database
db = SQLAlchemy(app)

# s3 variables
s3_bucket_name = app.config.get('S3_BUCKET')
s3_key = app.config.get('S3_KEY')
s3_secret = app.config.get('S3_SECRET')

# s3 client
s3_bucket_object = boto3.client("s3", aws_access_key_id=s3_key, aws_secret_access_key=s3_secret)
