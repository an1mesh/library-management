from flask import Flask
from sqlobject import connectionForURI,sqlhub
from flask_jwt_extended import JWTManager
from app.models import setup_db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    print(Config)
    jwt = JWTManager(app)
    setup_database(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app


def setup_database(app):
    connection = connectionForURI(app.config['DATABASE_URI'])
    print(app.config['DATABASE_URI'])
    sqlhub.processConnection = connection
    setup_db()

