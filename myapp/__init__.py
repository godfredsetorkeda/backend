import os
from flask import Flask 
from flask_cors import CORS  # Import CORS from flask_cors
from .extensions import dbA
from .routes import main

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    
    dbA.init_app(app)

    # Enable CORS for the entire app
    CORS(app)

    app.register_blueprint(main)

    return app
