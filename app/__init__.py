from flask import Flask, request, jsonify
from flask import redirect
from flask import render_template
from flask_login import login_user
from flask_login import logout_user
from flask_login import LoginManager
from app.database import db_session, init_db
from app.error_helper import InvalidUsage
from app.flask_firebase import FirebaseAuth
from app.main_page.view import blueprint_main
from app.my_oauth2_provider import my_oauth2_provider
from app.users_manager.models import User, Client, Grant, Token
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
login_manager = LoginManager()
auth = FirebaseAuth()


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    csrf.init_app(app)
    my_oauth2_provider.init_app(app)
    login_manager.init_app(app)
    auth.init_app(app)

    from app.users_manager.view import blueprint_applications
    app.register_blueprint(auth.blueprint, url_prefix='/authorize')
    app.register_blueprint(my_oauth2_provider.blueprint, url_prefix='/oauth')
    app.register_blueprint(blueprint_applications, url_prefix='/applications')
    app.register_blueprint(blueprint_main, url_prefix='/')

    csrf.exempt(my_oauth2_provider.blueprint)

    from app.api.users.view import blueprint_users
    app.register_blueprint(blueprint_users, url_prefix='/api/users')

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
            return response

        return render_template('error/401.html'), 401

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


init_db()


@auth.production_loader
def production_sign_in(token):
    account = User.query.filter_by(firebase_user_id=token['sub']).one_or_none()
    if account is None:
        account = User(firebase_user_id=token['sub'])
        account.email = token['email']
        account.email_verified = token['email_verified']
        account.name = token.get('name')
        account.photo_url = token.get('picture')
        account.admin_user = 0
        db_session.add(account)
        db_session.commit()
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
    return User.query.get(account_id)


@login_manager.unauthorized_handler
def authentication_required():
    return redirect('/')

