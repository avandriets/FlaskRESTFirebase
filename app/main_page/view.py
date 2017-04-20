from flask import Blueprint
from flask import current_app
from flask import render_template
from app.users_manager.models import current_user

blueprint_main = Blueprint('main_page', __name__)


@blueprint_main.route('/', methods=('GET',))
def home():
    user = current_user()
    return render_template('main_page.html', user=user,
                           firebase_auth=current_app.extensions['firebase_auth'])
