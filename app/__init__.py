from flask import Flask
from sqlobject import connectionForURI, sqlhub
from app.models import setup_db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    setup_database(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

def setup_database(app):
    connection = connectionForURI(app.config['DATABASE_URI'])
    sqlhub.processConnection = connection
    setup_db()

from app import routes