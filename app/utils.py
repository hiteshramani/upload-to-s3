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


def get_file_size(file_object):
    if file_object.content_length:
        return file_object.content_length

    try:
        position = file_object.tell()
        file_object.seek(0, 2)  # seek to end
        size = file_object.tell()
        file_object.seek(position)  # back to original position
        return size
    except (AttributeError, IOError):
        pass

    return 0
