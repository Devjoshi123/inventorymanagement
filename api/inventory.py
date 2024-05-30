# api/inventory.py
from flask_restful import Resource, reqparse
from models import db, Inventory
from flask_login import current_user, login_required

parser = reqparse.RequestParser()
parser.add_argument('item_name')
parser.add_argument('quantity')

class InventoryAPI(Resource):
    @login_required
    def get(self):
        items = Inventory.query.filter_by(user_id=current_user.id).all()
        return [{'id': item.id, 'item_name': item.item_name, 'quantity': item.quantity} for item in items]

    @login_required
    def post(self):
        args = parser.parse_args()
        item_name = args['item_name']
        quantity = args['quantity']
        new_item = Inventory(item_name=item_name, quantity=quantity, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        return {'message': 'Item added'}, 201

    @login_required
    def delete(self):
        args = parser.parse_args()
        item_id = args['id']
        item = Inventory.query.get(item_id)
        if item and item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            return {'message': 'Item deleted'}, 200
        return {'message': 'Item not found'}, 404
