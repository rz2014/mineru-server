from flask_sqlalchemy import SQLAlchemy
from .db import db
from flask_restful import fields
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # task id
    status = db.Column(db.String(16), nullable=True, server_default=db.text("init"))
    command = db.Column(db.String(255), nullable=False)
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    return_code = db.Column(db.Integer, nullable=True)
    create_at = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    update_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(
        self, id, status='init', command=None, output=None, error=None, return_code=None
    ):
        self.id = id
        self.status = status
        self.command = command
        self.output = output
        self.error = error
        self.return_code = return_code


task_fields = {
    'id': fields.String,
    'status': fields.String,
    'command': fields.String,
    'output': fields.String,
    'error': fields.String,
    'return_code': fields.Integer,
}
