from app import db
from argon2 import PasswordHasher
from requests import Response
from flask import request, url_for
import os
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel


hasher = PasswordHasher()
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
FROM_TITLE = "Stores REST API"
FROM_EMAIL = os.environ.get('EMAIL')


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    confirmation = db.relationship("ConfirmationModel", lazy='dynamic', cascade="all, delete-orphan")

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def validate_password(self, password: str):
        return hasher.verify(self.password, password)

    @staticmethod
    def set_password(password):
        return hasher.hash(password)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        link = request.url_root[:-1] + url_for("confirmation", confirmation_id=self.most_recent_confirmation.id)
        subject = "Registration confirmation"
        text = f"Please follow the link to confirm your registration: {link}"
        html = f'<html>Please follow the link to confirm your registration: <a href="{link}">{link}</a></html>'

        return Mailgun.send_email(self.email, subject, text, html)
