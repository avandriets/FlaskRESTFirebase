from flask import Flask, request, jsonify, redirect, render_template
from flask_login import login_user, logout_user, LoginManager
from app.database import db
from app.error_helper import InvalidUsage
from flask_wtf.csrf import CSRFProtect
from app.flask_firebase import FirebaseAuth
from app.my_oauth2_provider import my_oauth2_provider
from flask_uploads import (UploadSet, configure_uploads, IMAGES, UploadNotAllowed)

app = Flask(__name__)
app.config.from_object('config')

uploaded_photos = UploadSet('photos', IMAGES)
configure_uploads(app, uploaded_photos)

db.init_app(app)

csrf = CSRFProtect(app)
login_manager = LoginManager(app)
auth = FirebaseAuth(app)
my_oauth2_provider.init_app(app)

from app.users_manager.view import blueprint_applications
from app.main_page.view import blueprint_main

app.register_blueprint(auth.blueprint, url_prefix='/authorize')
app.register_blueprint(my_oauth2_provider.blueprint, url_prefix='/oauth')
app.register_blueprint(blueprint_applications, url_prefix='/applications')
app.register_blueprint(blueprint_main, url_prefix='/')

from app.api.users.view import blueprint_users

app.register_blueprint(blueprint_users, url_prefix='/api/profile')

# disable csrf protection for api urls
csrf.exempt(my_oauth2_provider.blueprint)
csrf.exempt(blueprint_users)


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    from app.database import init_db
    init_db()
    print('Initialized the database.')


@app.context_processor
def site_name():
    """
    inject site name in context
    :return:
    """
    return {'site_name': app.config['SITE_NAME']}


from flask_wtf.csrf import CSRFError


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    if '/api/' in request.path:
        response = jsonify({
            'status': 400,
            'sub_code': 1,
            'message': "csrf protection error"
        })
        return response, 400

    return render_template('error/csrf_error.html', reason=e.description), 400


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def not_found(error):
    """
    Simple 404 page
    :param error:
    :return:
    """
    return render_template('error/404.html'), 404


@app.errorhandler(403)
def not_found(error):
    """
    Simple 404 page
    :param error:
    :return:
    """
    return render_template('error/403.html'), 403


@app.errorhandler(401)
def not_found(error):
    """
    Simple 401 page
    :param error:
    :return:
    """
    if '/api/' in request.path:
        response = jsonify({
            'status': 401,
            'sub_code': 1,
            'message': "Client not authenticated."
        })
        return response, 401

    return render_template('error/401.html'), 401


@app.errorhandler(405)
def not_found(error):
    """
    Simple 401 page
    :param error:
    :return:
    """
    if '/api/' in request.path:
        response = jsonify({
            'status': 405,
            'sub_code': 1,
            'message': "Mehod nod allowed."
        })
        return response, 405

    return render_template('error/405.html'), 405


@app.teardown_appcontext
def shutdown_session(exception=None):
    from app.database import db
    db.session.remove()


@auth.production_loader
def production_sign_in(token):
    from app.users_manager.models import User
    account = User.query.filter_by(firebase_user_id=token['sub']).one_or_none()
    if account is None:
        account = User(firebase_user_id=token['sub'])
        account.email = token['email']
        account.email_verified = token['email_verified']
        account.name = token.get('name')
        account.photo_url = token.get('picture')
        account.admin_user = 0

        from app.database import db
        db.session.add(account)

        from app.api.profile.models import Profile
        profile = Profile(user=account)
        db.session.add(profile)

        db.session.commit()
    else:
        if account.admin_user == 0 or account.blocked:
            return False

    login_user(account)

    return True


@auth.unloader
def sign_out():
    logout_user()


@login_manager.user_loader
def load_user(account_id):
    from app.users_manager.models import User
    return User.query.get(account_id)


@login_manager.unauthorized_handler
def authentication_required():
    return redirect('/')
