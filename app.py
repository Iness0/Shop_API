from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from ma import ma
from config import Config
from blacklist import BLACKLIST
from libs.image_helper import IMAGE_SET
from flask_uploads import configure_uploads
from oauth import oauth


meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

db = SQLAlchemy(metadata=meta)
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    configure_uploads(app, IMAGE_SET)

    from resources.user import users_api
    app.register_blueprint(users_api)
    from resources.store import store_api
    app.register_blueprint(store_api)
    from resources.item import items_api
    app.register_blueprint(items_api)
    from resources.confirmation import confirmation_api
    app.register_blueprint(confirmation_api)
    from resources.image import images_api
    app.register_blueprint(images_api)
    from resources.git_login import github_api
    app.register_blueprint(github_api)
    from resources.order import order_api
    app.register_blueprint(order_api)

    return app


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    return jti in BLACKLIST


from models import item, store, user
