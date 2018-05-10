from flask import request, render_template, redirect, url_for, Blueprint, jsonify
import urllib

from app import app, s3_bucket_name, s3_bucket_object, db
from app.constants import ID_PARAMETER, KEY_ATTRIBUTE, CONTENTS_ATTRIBUTE, S3_WEBLINK_STRUCTURE, ACCEPTED_TYPES_LIST, \
    FILE_SIZE_THRESHOLD, FORCE_DOWNLOAD_SAVE_PATH
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
    return jsonify(list_object)


@app.route('/uploads/<int:id>', methods=['GET'])
def return_file_object(id):
    file_object = S3File.query.get(id)
    file_object = file_object.__dict__
    del file_object['_sa_instance_state']
    return jsonify(file_object)


@app.route('/uploads/<int:id>', methods=['DELETE'])
def delete_single_file(id):
    file_object = S3File.query.filter_by(id=id).with_entities(S3File.name).first()
    name = file_object[0]
    response_output = s3_bucket_object.delete_object(Bucket=s3_bucket_name, Key=name)
    return jsonify(response_output)


@app.route('/uploads', methods=['POST'])
def upload_files():
    files = request.files
    title = request.args.get('title')
    response_list = []
    for file_object in files.getlist('user_file[]'):
        # file size
        file_size = get_file_size(file_object)
        if file_size > FILE_SIZE_THRESHOLD:
            continue

        # file_mimetype
        file_mimetype = file_object.mimetype
        if file_mimetype not in ACCEPTED_TYPES_LIST:
            continue

        # file name
        file_name = file_object.filename

        # file extension
        file_extension = file_object.filename.rsplit('.', 1)[-1]

        # update db and upload file upload file
        try:
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
        except Exception:
            pass
    final_response_object = {'file_objects': response_list}
    return jsonify(final_response_object)


@app.route('/uploads/<int:id>/download', methods=['GET'])
def force_download_file(id):
    file_object = S3File.query.filter_by(id=id).with_entities(S3File.webLink, S3File.name).first()
    weblink = file_object[0]
    urllib.urlretrieve(weblink, FORCE_DOWNLOAD_SAVE_PATH.format(name=file_object.name))
    # more to be done here to verify the file and send appropriate output
    return jsonify({"output": "success"})
