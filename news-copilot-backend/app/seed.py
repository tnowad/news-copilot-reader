from datetime import datetime

from faker import Faker

from app.extensions import db
from app.models.article import Article
from app.models.category import Category
from app.models.role import Role, RoleEnum
from app.models.user import User

fake = Faker()


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
    categories = [
        {
            "id": i,
            "title": fake.word(),
            "slug": fake.slug(),
        }
        for i in range(10)
    ]

    for category in categories:
        category_entry = Category.query.filter_by(slug=category["slug"]).first()
        if not category_entry:
            category_entry = Category(
                title=category["title"],
                slug=category["slug"],
            )
            db.session.add(category_entry)


def seed_articles():

    articles = [
        {
            "id": i,
            "title": fake.sentence(),
            "cover_image": "https://i.pravatar.cc/150?img=4",
            "summary": fake.paragraph(),
            "slug": fake.slug(),
            "content": fake.text(),
            "category_ids": [1, 2],
            "author_id": 1,
        }
        for i in range(100)
    ]

    for article in articles:
        article_entry = Article.query.filter_by(title=article["title"]).first()
        if not article_entry:
            article_entry = Article(
                title=article["title"],
                cover_image=article["cover_image"],
                summary=article["summary"],
                slug=article["slug"],
                content=article["content"],
            )
            article_entry.author_id = article["author_id"]
            for category_id in article["category_ids"]:
                category = Category.query.get(category_id)
                if category:
                    article_entry.categories.append(category)

        db.session.add(article_entry)
        db.session.commit()


def seed_database():
    seed_roles()
    seed_users()
    seed_categories()
    seed_articles()
