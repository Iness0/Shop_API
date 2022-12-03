from collections import Counter
from flask import request, Blueprint
from flask_restful import Resource, Api
from libs.strings import gettext
from models.item import ItemModel
from models.order import OrderModel, ItemsInOrder
from schemas.order import OrderSchema


order_schema = OrderSchema()


class Order(Resource):
    @classmethod
    def get(cls):
        return order_schema.dump(OrderModel.find_all(), many=True), 200

    @classmethod
    def post(cls):
        """
        Get a token with item list. Connection to payment gateway must be made here.
        """
        data = request.get_json()
        items = []
        item_id_quantities = Counter(data["item_ids"])

        #counting items and retrieving them from db
        for _id, count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)
            if not item:
                return {"message": gettext("order_item_by_id_not_found").format(_id)}, 404

            items.append(ItemsInOrder(item_id=_id, quantity=count))

        order = OrderModel(items=items, status="pending")
        order.save_to_db()  # this does not submit to Stripe

        order.set_status("failed")
        #order.charge(data["token"])
        #order.set_status("complete")
        return order_schema.dump(order)


order_api = Blueprint("orders", __name__)
api = Api(order_api)
api.add_resource(Order, "/order")
