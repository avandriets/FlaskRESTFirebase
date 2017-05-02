from flask import Blueprint, abort, current_app, redirect, request, render_template, url_for, jsonify
from urllib.parse import urlparse

from app.jwt_parser import JwtParser

blueprint = Blueprint('firebase_auth', __name__)


@blueprint.route('/widget', methods={'GET', 'POST'})
def widget():
    return current_app.extensions['firebase_auth'].widget()


@blueprint.route('/sign-in', methods={'POST'})
def sign_in():
    response = current_app.extensions['firebase_auth'].sign_in()

    return jsonify(response=response)


@blueprint.route('/sign-out')
def sign_out():
    return current_app.extensions['firebase_auth'].sign_out()


class FirebaseAuth(JwtParser):
    PROVIDER_CLASSES = {
        'email': 'EmailAuthProvider',
        'facebook': 'FacebookAuthProvider',
        'github': 'GithubAuthProvider',
        'google': 'GoogleAuthProvider',
        'twitter': 'TwitterAuthProvider',
    }

    def __init__(self, app=None):
        JwtParser.__init__(self)

        self.debug = None
        self.api_key = None
        self.project_id = None
        self.provider_ids = None
        self.server_name = None
        self.production_load_callback = None
        self.development_load_callback = None
        self.unload_callback = None
        self.blueprint = blueprint
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['firebase_auth'] = self
        self.debug = app.debug

        self.api_key = app.config['FIREBASE_API_KEY']
        self.project_id = app.config['FIREBASE_PROJECT_ID']
        self.server_name = app.config['SERVER_NAME']
        provider_ids = []
        for name in app.config['FIREBASE_AUTH_SIGN_IN_OPTIONS'].split(','):
            class_name = self.PROVIDER_CLASSES[name.strip()]
            provider_id = 'firebase.auth.{}.PROVIDER_ID'.format(class_name)
            provider_ids.append(provider_id)
        self.provider_ids = ','.join(provider_ids)
        self.app = app

    def production_loader(self, callback):
        self.production_load_callback = callback
        return callback

    def development_loader(self, callback):
        self.development_load_callback = callback
        return callback

    def unloader(self, callback):
        self.unload_callback = callback
        return callback

    def url_for(self, endpoint, **values):
        full_endpoint = 'firebase_auth.{}'.format(endpoint)
        return url_for(
            full_endpoint,
            _external=True,
            _scheme='http',
            **values)

    def widget(self):
        return render_template('firebase/widget.html', firebase_auth=self)

    def sign_in(self):
        try:
            token = self.parse_key(request.data, app=self.app)
        except:
            return False

        response = self.production_load_callback(token)
        return response

    def sign_out(self):
        self.unload_callback()
        return redirect(self.verify_redirection())

    def verify_redirection(self):
        next_ = request.args.get('next')
        if not next_:
            return request.url_root
        if self.server_name:
            url = urlparse(next_)
            if not url.netloc.endswith(self.server_name):
                abort(400)
        return next_
