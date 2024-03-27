from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate

from app.extensions import db, jwt
from app.seed import seed_database

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["JWT_SECRET_KEY"] = "manager_access123"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=356)
    app.config["SQLALCHEMY_ECHO"] = True

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    with app.app_context():
        from .routes import routes_bp

        db.create_all()
        seed_database()

        app.register_blueprint(routes_bp)

        return app
