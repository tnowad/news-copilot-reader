from datetime import datetime
from app.models.role import Role, RoleEnum
from app.models.user import User
from app.extensions import db


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
            "bio": "I'm an admin user.",
            "birth_date": "1990-01-01",
            "phone_number": "1234567890",
            "roles": [RoleEnum.USER, RoleEnum.ADMIN],
        },
        {
            "email": "writer@example.com",
            "display_name": "Writer User",
            "avatar_image": "https://i.pravatar.cc/150?img=2",
            "password": "Password123",
            "bio": "I'm a writer user.",
            "birth_date": "1990-01-01",
            "phone_number": "1234567890",
            "roles": [RoleEnum.USER, RoleEnum.WRITER],
        },
        {
            "email": "user@example.com",
            "display_name": "Normal User",
            "avatar_image": "https://i.pravatar.cc/150?img=3",
            "password": "Password123",
            "bio": "I'm a user.",
            "birth_date": "1990-01-01",
            "phone_number": "1234567890",
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
                bio=user_map["bio"],
                birth_date=datetime.strptime(user_map["birth_date"], "%Y-%m-%d"),
                phone_number=user_map["phone_number"],
            )
            db.session.add(user)
            db.session.commit()

            for role_enum in user_map["roles"]:
                role = Role.query.filter_by(name=role_enum.value).first()
                if role:
                    user.roles.append(role)
            db.session.commit()


def seed_categories():
    pass


def seed_articles():
    pass


def seed_database():
    seed_roles()
    seed_users()
    seed_categories()
    seed_articles()
