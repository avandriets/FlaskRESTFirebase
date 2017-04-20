from flask import Blueprint, jsonify
from flask import request
from app import InvalidUsage
from app import my_oauth2_provider

blueprint_users = Blueprint('users', __name__)


@blueprint_users.route('/me')
@my_oauth2_provider.require_oauth()
def me():
    # user = request.oauth.user
    try:
        # user = current_user()
        user = request.oauth.user
        response = jsonify(username=user.name)
        return response
    except:
        raise InvalidUsage('There occurs an error.', status_code=500)


# @blueprint_users.route('/restaurants/<int:id>', methods=['GET', 'PUT', 'DELETE'])
# def restaurant_handler(id):
#     restaurant = session.query(Restaurant).filter_by(id=id).one()
#     if request.method == 'GET':
#         # RETURN A SPECIFIC RESTAURANT
#         return jsonify(restaurant=restaurant.serialize)
#     elif request.method == 'PUT':
#         # UPDATE A SPECIFIC RESTAURANT
#         address = request.args.get('address')
#         image = request.args.get('image')
#         name = request.args.get('name')
#         if address:
#             restaurant.restaurant_address = address
#         if image:
#             restaurant.restaurant_image = image
#         if name:
#             restaurant.restaurant_name = name
#         session.commit()
#         return jsonify(restaurant=restaurant.serialize)
#
#     elif request.method == 'DELETE':
#         # DELETE A SPECFIC RESTAURANT
#         session.delete(restaurant)
#         session.commit()
#         return "Restaurant Deleted"
