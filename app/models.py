# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from datetime import datetime


# Define a base model for other database tables to inherit
class S3File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    extension = db.Column(db.String)
    title = db.Column(db.String)
    name = db.Column(db.String)
    mimeType = db.Column(db.String)
    webLink = db.Column(db.String)
    size = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    is_private = db.Column(db.Boolean, default=False)
