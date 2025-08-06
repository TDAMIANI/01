from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy without app to allow factory pattern
db = SQLAlchemy()


def create_app(database_uri='sqlite:///axi.db'):
    """Application factory for the AXI app.

    Parameters
    ----------
    database_uri: str
        URI for the database connection. Defaults to a local SQLite file.
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import and register blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app
