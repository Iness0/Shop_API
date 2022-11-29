from ma import ma
from models.user import UserModel
from marshmallow import pre_dump


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        load_only = ("password",)
        dump_only = ("id", "confirmation")

    @pre_dump
    def _pre_dump(self, user: UserModel):
        user.confirmation = [user.most_recent_confirmation]
        return user