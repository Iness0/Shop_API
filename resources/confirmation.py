import traceback
from time import time
from flask import make_response, render_template, Blueprint
from flask_restful import Resource, Api
from libs.strings import gettext
from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema


confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": gettext("confirmation_not_found")}, 404
        if confirmation.expired:
            return {"message": gettext("confirmation_link_expired")}, 400
        if confirmation.confirmed:
            return {"message": gettext("confirmation_already_confirmed")}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email), 200, headers
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """Testing only"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        return (
            {
                "current_time": int(time()),
                "confirmation": [confirmation_schema.dump(i)
                                 for i in user.confirmation.order_by(ConfirmationModel.expire_at)],
            }, 200,
        )

    @classmethod
    def post(cls, user_id: int):
        """Resend confirmation"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("confirmation_resend_successful")}, 201
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": gettext("confirmation_resend_fail")}, 500


confirmation_api = Blueprint('confirmation', __name__)
api = Api(confirmation_api)
api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
