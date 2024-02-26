from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .routes import routes_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

app.register_blueprint(routes_bp)
