import pytest
from app.models.user import User
from app.models.role import Role, RoleEnum
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
from app.models.bookmark import Bookmark
from app.models.view import View
from app.models.report import Report
from app.extensions import db, bcrypt
from app.errors.validation_error import ValidationError


class TestUserModel:
    def test_create_user(self, session):
        user = User(
            email="test@example.com",
            display_name="Test User",
        )
        user.set_password("password123")
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"

    def test_password_hashing(self):
        user = User(email="hash@example.com", display_name="Hash User")
        user.set_password("mypassword")

        assert user.password != "mypassword"
        assert user.check_password("mypassword") is True
        assert user.check_password("wrongpassword") is False

    def test_user_roles(self, session):
        user = User(email="roletest@example.com", display_name="Role User")
        user.set_password("pass123")

        admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
        user_role = Role.query.filter_by(name=RoleEnum.USER).first()
        user.roles.append(admin_role)
        user.roles.append(user_role)

        session.add(user)
        session.commit()

        assert user.has_role("ADMIN") is True
        assert user.has_role("USER") is True
        assert user.has_role("WRITER") is False

    def test_user_email_validation(self, session):
        user = User(email="", display_name="Bad Email")
        with pytest.raises(ValidationError, match="Email cannot be empty"):
            session.add(user)
            session.commit()

    def test_user_display_name_validation(self, session):
        user = User(email="name@test.com", display_name="")
        with pytest.raises(ValidationError, match="Display name cannot be empty"):
            session.add(user)
            session.commit()

    def test_user_unique_email(self, session):
        user1 = User(email="unique@example.com", display_name="First")
        user1.set_password("pass1")
        session.add(user1)
        session.commit()

        user2 = User(email="unique@example.com", display_name="Second")
        user2.set_password("pass2")
        session.add(user2)

        with pytest.raises(Exception):
            session.commit()

    def test_user_repr(self):
        user = User(email="repr@example.com", display_name="Repr")
        assert "repr@example.com" in repr(user)


class TestArticleModel:
    def test_create_article(self, session):
        article = Article(
            title="Test Article",
            slug="test-article",
            content="This is the content.",
            summary="A summary.",
        )
        session.add(article)
        session.commit()

        assert article.id is not None
        assert article.title == "Test Article"
        assert article.slug == "test-article"

    def test_article_title_validation(self, session):
        article = Article(title="", slug="test-slug", content="content")
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            session.add(article)
            session.commit()

    def test_article_content_validation(self, session):
        article = Article(title="Title", slug="test-slug", content="")
        with pytest.raises(ValidationError, match="Content cannot be empty"):
            session.add(article)
            session.commit()

    def test_article_summary_length_validation(self, session):
        long_summary = "A" * 2001
        article = Article(
            title="Title",
            slug="test-slug",
            content="content",
            summary=long_summary,
        )
        with pytest.raises(ValidationError, match="Summary is too long"):
            session.add(article)
            session.commit()

    def test_article_author_relationship(self, session):
        user = User(email="author@example.com", display_name="Author")
        user.set_password("pass123")
        session.add(user)
        session.commit()

        article = Article(
            title="My Article",
            slug="my-article",
            content="content",
            author_id=user.id,
        )
        session.add(article)
        session.commit()

        assert article.author == user
        assert article in user.articles

    def test_article_repr(self, session):
        article = Article(title="Repr Article", slug="repr-article", content="content")
        session.add(article)
        session.commit()

        assert "Repr Article" in repr(article)


class TestCategoryModel:
    def test_create_category(self, session):
        category = Category(
            title="Technology",
            slug="technology",
            description="Tech news",
        )
        session.add(category)
        session.commit()

        assert category.id is not None
        assert category.title == "Technology"


class TestCommentModel:
    def test_create_comment(self, session):
        user = User(email="commenter@example.com", display_name="Commenter")
        user.set_password("pass123")
        session.add(user)
        session.commit()

        article = Article(
            title="Article",
            slug="article",
            content="content",
            author_id=user.id,
        )
        session.add(article)
        session.commit()

        comment = Comment(
            content="Great article!",
            author_id=user.id,
            article_id=article.id,
        )
        session.add(comment)
        session.commit()

        assert comment.id is not None
        assert comment.content == "Great article!"


class TestBookmarkModel:
    def test_create_bookmark(self, session):
        user = User(email="bookmarker@example.com", display_name="Bookmarker")
        user.set_password("pass123")
        session.add(user)
        session.commit()

        article = Article(
            title="Bookmarkable",
            slug="bookmarkable",
            content="content",
            author_id=user.id,
        )
        session.add(article)
        session.commit()

        bookmark = Bookmark(user_id=user.id, article_id=article.id)
        session.add(bookmark)
        session.commit()

        assert bookmark.id is not None


class TestRoleModel:
    def test_role_enum_values(self):
        assert RoleEnum.USER.value == "USER"
        assert RoleEnum.WRITER.value == "WRITER"
        assert RoleEnum.ADMIN.value == "ADMIN"

    def test_role_creation(self, session):
        role = Role(name=RoleEnum.WRITER)
        session.add(role)
        session.commit()

        assert role.id is not None
        assert role.name == RoleEnum.WRITER
