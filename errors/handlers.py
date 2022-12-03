from flask import jsonify, current_app
from marshmallow import ValidationError


@current_app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400