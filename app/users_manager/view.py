from flask import Blueprint, request
from flask import abort
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import login_required
from werkzeug.security import gen_salt
from app.database import db_session
from app.users_manager.models import current_user, Client

blueprint_applications = Blueprint('oauth2', __name__)


def get_applications_list(user_param):
    return db_session.query(Client).filter_by(user=user_param)


@blueprint_applications.route('/new-app/', methods=['GET', 'POST'])
@login_required
def create_application():
    user = current_user()

    context = {'user': user}

    if request.method == 'POST':
        try:
            name = request.form['name']
        except Exception:
            name = None
        try:
            description = request.form['description']
        except Exception:
            description = None
        try:
            client_id = request.form['client_id']
        except Exception:
            client_id = None
        try:
            client_secret = request.form['client_secret']
        except Exception:
            client_secret = None
        try:
            redirect_uris = request.form['redirect_uris']
        except Exception:
            redirect_uris = None
        try:
            default_scopes = request.form['default_scopes']
        except Exception:
            default_scopes = None

        context['name'] = name
        context['description'] = description
        context['client_id'] = client_id
        context['client_secret'] = client_secret
        context['redirect_uris'] = redirect_uris
        context['default_scopes'] = default_scopes

        if not (name and name.strip()):
            context['error'] = "You should input application name"
            return render_template("applications/new_application.html", **context)

        if not (description and description.strip()):
            context['error'] = "You should input description"
            return render_template("applications/new_application.html", **context)

        if not (client_id and client_id.strip()):
            context['error'] = "You should input client id"
            return render_template("applications/new_application.html", **context)

        if not (client_secret and client_secret.strip()):
            context['error'] = "You should input client secret"
            return render_template("applications/new_application.html", **context)

        if not (redirect_uris and redirect_uris.strip()):
            context['error'] = "You should input redirect_uris"
            return render_template("applications/new_application.html", **context)

        if not (default_scopes and default_scopes.strip()):
            context['error'] = "You should input default scopes"
            return render_template("applications/new_application.html", **context)

        new_application = Client(
            application_name=name,
            application_description=description,
            client_id=client_id,
            client_secret=client_secret,
            _redirect_uris=redirect_uris,
            _default_scopes=default_scopes,
            user_id=user.id,
        )

        db_session.add(new_application)
        db_session.commit()

        return redirect(url_for('oauth2.applications_list'))

    else:
        try:
            name = request.form['name']
        except Exception:
            name = None
        try:
            description = request.form['description']
        except Exception:
            description = None
        try:
            client_id = request.form['client_id']
        except Exception:
            client_id = None
        try:
            client_secret = request.form['client_secret']
        except Exception:
            client_secret = None
        try:
            redirect_uris = request.form['redirect_uris']
        except Exception:
            redirect_uris = None
        try:
            default_scopes = request.form['default_scopes']
        except Exception:
            default_scopes = None

        if not client_id:
            client_id = gen_salt(40)

        if not client_secret:
            client_secret = gen_salt(50)

        if not redirect_uris:
            redirect_uris = ' '.join([
                'http://localhost:8000/authorized',
                'http://127.0.0.1:8000/authorized',
                'http://127.0.1:8000/authorized',
                'http://127.1:8000/authorized',
            ])

        if not default_scopes:
            default_scopes = 'email'

        context['client_id'] = client_id
        context['client_secret'] = client_secret
        context['redirect_uris'] = redirect_uris
        context['default_scopes'] = default_scopes

        return render_template("applications/new_application.html", **context)


@blueprint_applications.route('/all/', methods=('GET',))
@login_required
def applications_list():
    user = current_user()
    return render_template('applications/applications.html', user=user, applications=get_applications_list(user))


@blueprint_applications.route('/<string:application_id>/', methods=('GET',))
@login_required
def application_item(application_id):
    user = current_user()
    context = {'user': user}
    application = db_session.query(Client).filter_by(user=user, client_id=application_id).one()

    if application:
        context['name'] = application.application_name
        context['description'] = application.application_description
        context['client_id'] = application.client_id
        context['client_secret'] = application.client_secret
        context['redirect_uris'] = application._redirect_uris
        context['default_scopes'] = application._default_scopes
        return render_template("applications/application_detail.html", **context)
    else:
        abort(404)
