# Run a test server.
# from app import app
from app import create_app

create_app('config').run(host='127.0.0.1', port=8000)
