from . import db
from sqlalchemy import func, cast, String
from datetime import datetime


class users(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    c_full_name = db.Column(db.String(150), nullable=False)
    c_username = db.Column(db.String(30), unique=True, nullable=False)
    c_password = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)


class managers(db.Model):
    manager_id = db.Column(db.Integer, primary_key=True)
    m_full_name = db.Column(db.String(255), nullable=False)
    m_username = db.Column(db.String(50), unique=True, nullable=False)
    m_password = db.Column(db.String(50), nullable=False)


class transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.client_id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.client_id', ondelete='CASCADE'), nullable=True)