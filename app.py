# -*- coding: utf-8 -*-

from flask import Flask
from routes import Routes
from auth import Authentication
from db import cleanup
import os
import atexit
from file_operations import FileClass


import os
from flask import Flask # or from fastapi import FastAPI

app = Flask(__name__)

if __name__ == "__main__":
    # Heroku provides the port via the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

