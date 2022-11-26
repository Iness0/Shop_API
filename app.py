from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from ma import ma
from config import Config
from blacklist import BLACKLIST

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from resources.user import users_api
    app.register_blueprint(users_api)
    from resources.store import store_api
    app.register_blueprint(store_api)
    from resources.item import items_api
    app.register_blueprint(items_api)

    return app


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    return jti in BLACKLIST


from models import item, store, user
