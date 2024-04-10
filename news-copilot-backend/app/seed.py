from datetime import datetime

from faker import Faker

from app.extensions import db
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
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
            "description": fake.paragraph(),
            "title": fake.word(),
            "slug": fake.slug(),
        }
        for i in range(10)
    ]

    for category in categories:
        category_entry = Category.query.filter_by(id=category["id"]).first()
        if not category_entry:
            category_entry = Category(
                description=category["description"],
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
            "content": "".join(fake.text() for _ in range(100)),
            "category_ids": fake.random_elements(
                elements=range(10), length=3, unique=True
            ),
            "author_id": 1,
        }
        for i in range(1, 101)
    ]

    for article in articles:
        article_entry = Article.query.filter_by(id=article["id"]).first()
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

            for _ in range(5):
                comment = Comment(
                    content=fake.paragraph(),
                    author_id=1,
                    article_id=article["id"],
                )
                db.session.add(comment)

        db.session.add(article_entry)
        db.session.commit()


def seed_database():
    seed_roles()
    seed_users()
    seed_categories()
    seed_articles()
