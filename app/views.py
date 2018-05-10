from flask import request, render_template, redirect, url_for, Blueprint, jsonify
import json
import copy

from app import app, s3_bucket_name, s3_bucket_object, db
from app.constants import ID_PARAMETER, KEY_ATTRIBUTE, CONTENTS_ATTRIBUTE, S3_WEBLINK_STRUCTURE
from app.utils import upload_to_s3, get_file_size
from app.models import S3File

upload_to_s3_view = Blueprint('upload_to_s3_view', __name__)


@app.route('/')
def upload_index():
    return render_template('upload.html')


@app.route('/uploads', methods=['GET'])
def list_bucket_files():
    objects = s3_bucket_object.list_objects(Bucket=s3_bucket_name)
    bucket_files_list = [file_object[KEY_ATTRIBUTE] for file_object in objects[CONTENTS_ATTRIBUTE]]
    list_object = {
        "bucket_files_list": bucket_files_list
    }
    return json.dumps(list_object)


@app.route('/uploads', methods=['DELETE'])
def delete_single_file():
    key = request.args.get(ID_PARAMETER)
    output = s3_bucket_object.delete_object(Bucket=s3_bucket_name, Key=key)
    print output
    return json.dumps(output)


@app.route('/uploads', methods=['POST'])
def upload_files():
    files = request.files
    title = request.args.get('title')
    response_list = []
    for file_object in files.getlist('user_file[]'):
        # file size
        file_size = get_file_size(file_object)

        # file_mimetype
        file_mimetype = file_object.mimetype

        # file name
        file_name = file_object.filename

        # file extension
        file_extension = file_object.filename.rsplit('.', 1)[-1]

        # upload file
        upload_to_s3(s3_bucket_object, file_object, s3_bucket_name)
        file_schema = S3File(extension=file_extension, title=title, name=file_name,
                             mimeType=file_mimetype, size=file_size,
                             webLink=S3_WEBLINK_STRUCTURE.format(bucket_name=s3_bucket_name,
                                                                 file_name=file_name))
        db.session.add(file_schema)
        db.session.commit()
        response_object = S3File.query.filter_by(name=file_name).first()
        response_object = response_object.__dict__
        del response_object['_sa_instance_state']
        response_list.append(response_object)
    final_response_object = {'file_objects': response_list}
    return jsonify(final_response_object)
