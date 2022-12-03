from flask_restful import Resource, Api
from flask import request, Blueprint, g, url_for
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token
from oauth import oauth
from libs.strings import gettext
from models.user import UserModel


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        redirect = url_for('github_login.authorize', _external=True)
        return oauth.github.authorize_redirect(redirect)


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        token = oauth.github.authorize_access_token()
        print(token)
        if token is None:
            return {"error": gettext("token_failure")}, 401
        resp = oauth.github.get('user')
        resp.raise_for_status()
        profile = resp.json()
        print(profile)
        username = profile['login']
        user = UserModel.find_by_username(username)
        if not user:
            user = UserModel(username=username,  password=None)
            user.save_to_db()
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}, 200


github_api = Blueprint('github_login', __name__)
api = Api(github_api)
api.add_resource(GithubLogin, "/login/github")
api.add_resource(GithubAuthorize, "/login/github/authorized", endpoint="authorize")
