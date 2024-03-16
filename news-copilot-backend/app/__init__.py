from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    db.init_app(app)
    with app.app_context():
        from .routes import routes_bp

        app.register_blueprint(routes_bp)
        return app
