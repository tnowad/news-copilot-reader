from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    with app.app_context():
        from .routes import routes_bp

        db.create_all()

        app.register_blueprint(routes_bp)

        return app
