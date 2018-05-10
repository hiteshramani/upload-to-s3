from app.constants import ACL_PERMISSION


def upload_to_s3(s3_bucket_object, file_object, s3_bucket_name):
    s3_bucket_object.upload_fileobj(
        file_object,
        s3_bucket_name,
        file_object.filename,
        ExtraArgs={
            "ACL": ACL_PERMISSION,
            "ContentType": file_object.content_type
        }
    )
