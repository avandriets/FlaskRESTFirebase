# Flask REST api with Firebase auth.
Source code for a "Flask REST api with Firebase auth" project.
It is a prototype of project that can be a basement for REST service.
There are used such technologies as Flask, SQLAlchemy, Firebase, OAuth2

## How to start project
1. Fill firebase your project credentials to config.js and to config.py
3. Set grant type that you need to  users_manager/models.py Client.allowed_grant_types
4. Start the project
```
$ python /vagrant/catalog/application.py
```
5. Make administrative account to get access to site (kind of admin panel)
 After first attempt of login an user account appears in the database, put 1 to the field "admin_user",
 if you need to block the user put 1 to the field "block" do not forget to save changes.

## How to get token

1. Fill request parameters
```
grant_type: password
client_id: [CLIENT ID]
client_secret: [CLIENT SECRET]
username: [ANYTHING]
password: [ANYTHING]
firebase_token: [JWT TOKEN]
```
2. to get token go to URL http://127.0.0.1:8000/oauth/token
you get such json
```
{
 "refresh_token": "6WkB5Gt2L3h6YCiZMdE5WLLff45P1x",
 "token_type": "Bearer",
 "scope": "email",
 "access_token": "SNabPWS9F6ZBEpf6VvaZDE4v8Bv1wb"
}
```


## How to get data from rest service

1. Put to request parameters access token
```
access_token : [YOUR TOKEN]
```
2. Go to api URL for example http://127.0.0.1:8000/api/users/me


## How to manage migrations

1. Initalization
```
EnvFlaskFirebase/bin/python3 manage.py db init
```

2. Migrate
```
EnvFlaskFirebase/bin/python3 manage.py db migrate
```

3. Update
```
EnvFlaskFirebase/bin/python3 manage.py db upgrade
```

4. Help
```
EnvFlaskFirebase/bin/python3 manage.py db --help
```