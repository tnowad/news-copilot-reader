from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate

from app.db import db
from app.jwt import jwt
from app.models.role import Role, RoleEnum
from app.models.user import User

migrate = Migrate()


def seed_roles():
    for role in RoleEnum:
        role_entry = Role.query.filter_by(name=role.value).first()
        if not role_entry:
            role_entry = Role(name=role.value)
            db.session.add(role_entry)
    db.session.commit()


def seed_users():
    user_role_maps = [
        {
            "email": "admin@example.com",
            "display_name": "Admin User",
            "avatar_image": "https://i.pravatar.cc/150?img=1",
            "password": "Password123",
            "roles": [RoleEnum.USER, RoleEnum.ADMIN],
        },
        {
            "email": "writer@example.com",
            "display_name": "Writer User",
            "avatar_image": "https://i.pravatar.cc/150?img=2",
            "password": "Password123",
            "roles": [RoleEnum.USER, RoleEnum.WRITER],
        },
        {
            "email": "user@example.com",
            "display_name": "Normal User",
            "avatar_image": "https://i.pravatar.cc/150?img=3",
            "password": "Password123",
            "roles": [RoleEnum.USER],
        },
    ]

    for user_map in user_role_maps:
        user = User.query.filter_by(email=user_map["email"]).first()
        if not user:
            user = User(
                email=user_map["email"],
                display_name=user_map["display_name"],
                avatar_image=user_map["avatar_image"],
                password=user_map["password"],
            )
            db.session.add(user)
            db.session.commit()

            for role_enum in user_map["roles"]:
                role = Role.query.filter_by(name=role_enum.value).first()
                if role:
                    user.roles.append(role)
            db.session.commit()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["JWT_SECRET_KEY"] = "manager_access123"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=356)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    with app.app_context():
        from .routes import routes_bp

        db.create_all()
        seed_roles()
        seed_users()

        app.register_blueprint(routes_bp)

        return app
