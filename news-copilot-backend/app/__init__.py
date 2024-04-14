from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate

from app.extensions import cache, db, jwt, mail
from app.seed import seed_database
from flask_mail import Message

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["JWT_SECRET_KEY"] = "manager_access123"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=356)
    app.config["MAIL_SERVER"] = "localhost"
    app.config["MAIL_PORT"] = 1025
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = None
    app.config["MAIL_PASSWORD"] = None
    app.config["MAIL_DEFAULT_SENDER"] = "news-copilot-reader@example.com"

    # app.config["SQLALCHEMY_ECHO"] = True

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    cache.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from .routes import routes_bp

        # Send a test email
        msg = Message("Hello from Flask-Mail", recipients=["recipient@example.com"])
        msg.body = "This is a test email sent from Flask using Maildev."
        mail.send(msg)

        db.create_all()
        seed_database()

        app.register_blueprint(routes_bp)

        return app
