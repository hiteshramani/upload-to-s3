from app import app
from app.views import upload_to_s3_view

if __name__ == '__main__':
    app.register_blueprint(upload_to_s3_view)
    app.run(debug=True)
