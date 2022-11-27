import traceback
from http.client import NOT_FOUND
from time import time
from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

USER_NOT_FOUND = "User not found"
EXPIRED = "Your confirmation link has expired"
ALREADY_CONFIRMED = "This user has already been confirmed"
confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": USER_NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_path.html", email=confirmation.user.email), 200, headers
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(self, user_id: int):
        """Testing only"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return (
            {
                "current_time": int(time()),
                "confirmation": [confirmation_schema.dump(i)
                                 for i in user.confirmation.order_by(ConfirmationModel.expire_at)],
            }, 200,
        )

    @classmethod
    def post(self, user_id: int):
        """Resend confirmation"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "Resend was successful"}, 201
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": "Resend has failed"}, 500

