from flask import session
from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy import event
from sqlalchemy.orm import relationship
from app.database import db


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    firebase_user_id = Column(Text, unique=True)
    email = Column(Text, unique=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    name = Column(Text)
    photo_url = Column(Text)
    admin_user = Column(Integer, unique=False, default=0, nullable=False)
    blocked = Column(Integer, unique=False, default=0, nullable=False)

    def get_id(self):
        return self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email
        }


class Client(db.Model):
    __tablename__ = 'Client'

    application_name = Column(String(100))
    application_description = Column(Text)
    client_id = Column(String(40), primary_key=True)
    client_secret = Column(String(55), nullable=False)

    user_id = Column(ForeignKey('User.id'))
    user = relationship('User')

    _redirect_uris = Column(Text)
    _default_scopes = Column(Text)

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    @property
    def allowed_grant_types(self):
        # all posible grant types
        # 'authorization_code', 'password',
        # 'client_credentials', 'refresh_token',
        # put that grant type that you need for all applications
        return ['password']


class Grant(db.Model):
    __tablename__ = 'Grant'

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, ForeignKey('User.id', ondelete='CASCADE')
    )
    user = relationship('User')

    client_id = Column(
        String(40), ForeignKey('Client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    code = Column(String(255), index=True, nullable=False)

    redirect_uri = Column(String(255))
    expires = Column(DateTime)

    _scopes = Column(Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    __tablename__ = 'Token'

    id = Column(Integer, primary_key=True)
    client_id = Column(
        String(40), ForeignKey('Client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    user_id = Column(
        Integer, ForeignKey('User.id')
    )
    user = relationship('User')

    # currently only bearer is supported
    token_type = Column(String(40))

    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)
    expires = Column(DateTime)
    _scopes = Column(Text)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


def current_user():
    if 'user_id' in session:
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).one_or_none()
    else:
        user = None

    return user


@event.listens_for(User, 'after_insert')
def receive_user_after_insert(mapper, connection, target):
    pass
    # try:
    #     profile = Profile(user = target)
    #     profile.user = target
    #     db.session.add(profile)
    # except SQLAlchemyError as ex:
    #     print(ex)
