from jwt import ExpiredSignatureError
from datetime import timedelta, datetime
from flask import Blueprint
from flask_oauthlib.provider import OAuth2Provider
from app import InvalidUsage
from app.database import db_session
from app.jwt_parser import JwtParser
from app.users_manager.models import current_user, Client, Grant, Token, User

blueprint = Blueprint('my_oauth2_provider', __name__)


class MyOauth2Provider(OAuth2Provider, JwtParser):
    def __init__(self, app=None):
        super().__init__(app=None)
        JwtParser.__init__(self)

        self.blueprint = blueprint

    def _clientgetter(self, client_id):
        return Client.query.filter_by(client_id=client_id).first()

    def _grantgetter(self, client_id, code):
        return Grant.query.filter_by(client_id=client_id, code=code).first()

    def _tokensetter(self, token, request, *args, **kwargs):
        toks = Token.query.filter_by(
            client_id=request.client.client_id,
            user_id=request.user.id
        )

        # make sure that every client has only one token connected to a user
        for t in toks:
            db_session.delete(t)
            db_session.commit()

        expires_in = token.pop('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        tok = Token(
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            token_type=token['token_type'],
            _scopes=token['scope'],
            expires=expires,
            client_id=request.client.client_id,
            user_id=request.user.id,
        )

        db_session.add(tok)
        db_session.commit()
        return tok

    def _grantsetter(self, client_id, code, request, *args, **kwargs):
        # decide the expires time yourself
        expires = datetime.utcnow() + timedelta(seconds=100)
        grant = Grant(
            client_id=client_id,
            code=code['code'],
            redirect_uri=request.redirect_uri,
            _scopes=' '.join(request.scopes),
            user=current_user(),
            expires=expires
        )
        db_session.add(grant)
        db_session.commit()
        return grant

    def _tokengetter(self, access_token=None, refresh_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        elif refresh_token:
            return Token.query.filter_by(refresh_token=refresh_token).first()

    def _usergetter(self, username, password, client, request, *args, **kwargs):
        token = request.jwt_token
        try:
            result = self.parse_key(token_data=token, app=self.app)
        except ExpiredSignatureError:
            raise InvalidUsage('Token expired', status_code=500)

        account = User.query.filter_by(firebase_user_id=result['sub']).one_or_none()
        if account is None:
            account = User(firebase_user_id=token['sub'])
            account.email = token['email']
            account.email_verified = token['email_verified']
            account.name = token.get('name')
            account.photo_url = token.get('picture')
            account.admin_user = 0
            db_session.add(account)
            db_session.commit()

        if account and account.blocked == 1:
            raise InvalidUsage('Access denied', status_code=403)

        return account


my_oauth2_provider = MyOauth2Provider()


@blueprint.route('/token', methods=['POST'])
@my_oauth2_provider.token_handler
def my_access_token():
    # You can put extra data to request that return to user
    return None


@blueprint.route('/errors')
@my_oauth2_provider.token_handler
def error_by_oauth():
    raise InvalidUsage('There occurs an error.', status_code=500)
