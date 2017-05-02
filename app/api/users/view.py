from flask import Blueprint, jsonify
from flask import request
from app import my_oauth2_provider
from app.error_helper import InvalidUsage

blueprint_users = Blueprint('users', __name__)


@blueprint_users.route('/me')
@my_oauth2_provider.require_oauth()
def me():
    try:
        user = request.oauth.user
        response = jsonify(username=user.name)
        return response
    except:
        raise InvalidUsage('There occurs an error.', status_code=500)

