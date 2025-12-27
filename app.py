# -*- coding: utf-8 -*-

from flask import Flask
from routes import Routes
from auth import Authentication
from db import cleanup
import os
import atexit
from file_operations import FileClass


def create_app(config_path: str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_path)
    Routes(app)
    Authentication(app)
    return app

def run_local_development():
    """Run the app in local development mode"""
    file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'test')
    app = create_app('config.Config')
    FileClass(app, file_path)
    atexit.register(cleanup)
    app.run(debug=True)

def run_production():
    """Run the app in production mode"""
    app = create_app("config.Config")
    bucket_path = os.getenv("BUCKET_PATH", "path for the bucket")
    FileClass(app, bucket_path)
    app.run()

if __name__ == "__main__":
    if os.getenv('FLASK_ENV') == 'development':
        run_local_development()
    else:
        run_production()
