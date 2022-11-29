from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage
import typing


class FileStorageField(fields.Field):
    default_error_messages = {{"invalid": "Not a valid image"}}

    def _deserialize(
        self,
        value: typing.Any,
        attr: str | None,
        data: typing.Mapping[str, typing.Any] | None,
        **kwargs,
    ) -> FileStorage:

        if value is None:
            return None

        elif not isinstance(value, FileStorageField):
            self.fail("invalid")
        else:
            return value


class ImageSchema(Schema):
    image = FileStorageField(required=True)
