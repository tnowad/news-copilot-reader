import pytest
from http import HTTPStatus
from app.models.article import Article
from app.models.category import Category
from app.models.user import User


class TestArticleEndpoints:
    def test_get_articles(self, client, auth_headers, session):
        user = User.query.filter_by(email="testuser@example.com").first()
        category = Category(title="Tech", slug="tech")
        session.add(category)
        session.commit()

        article = Article(
            title="Test Article",
            slug="test-article",
            content="Article content here.",
            summary="Summary",
            author_id=user.id,
        )
        article.categories.append(category)
        session.add(article)
        session.commit()

        response = client.get("/articles/", headers=auth_headers)
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["success"] is True
        assert len(data["data"]["articles"]) >= 1

    def test_create_article(self, client, auth_headers, session):
        response = client.post("/articles/", headers=auth_headers, json={
            "title": "New Article",
            "content": "New content",
            "summary": "A new summary",
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.CREATED
        assert data["success"] is True
        assert "new" in data["data"]["title"].lower()

    def test_create_article_without_auth(self, client):
        response = client.post("/articles/", json={
            "title": "No Auth",
            "content": "Should fail",
        })
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_single_article(self, client, auth_headers, session):
        user = User.query.filter_by(email="testuser@example.com").first()
        article = Article(
            title="Single Article",
            slug="single-article",
            content="Content",
            author_id=user.id,
        )
        session.add(article)
        session.commit()

        response = client.get(
            f"/articles/{article.slug}/{article.id}",
            headers=auth_headers,
        )
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["data"]["title"] == "Single Article"

    def test_get_nonexistent_article(self, client, auth_headers):
        response = client.get("/articles/nope/99999", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_article(self, client, auth_headers, session):
        user = User.query.filter_by(email="testuser@example.com").first()
        article = Article(
            title="Original Title",
            slug="original-title",
            content="Original content",
            author_id=user.id,
        )
        session.add(article)
        session.commit()

        response = client.put(
            f"/articles/{article.slug}/{article.id}",
            headers=auth_headers,
            json={"title": "Updated Title", "content": "Updated content"},
        )
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["data"]["title"] == "Updated Title"

    def test_delete_article(self, client, auth_headers, session):
        user = User.query.filter_by(email="testuser@example.com").first()
        article = Article(
            title="Delete Me",
            slug="delete-me",
            content="content",
            author_id=user.id,
        )
        session.add(article)
        session.commit()

        response = client.delete(
            f"/articles/{article.slug}/{article.id}",
            headers=auth_headers,
        )
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK


class TestCategoryEndpoints:
    def test_get_categories(self, client, auth_headers, session):
        category = Category(title="Science", slug="science")
        session.add(category)
        session.commit()

        response = client.get("/categories/", headers=auth_headers)
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["success"] is True

    def test_create_category_as_admin(self, client, admin_headers):
        response = client.post("/categories/", headers=admin_headers, json={
            "title": "New Category",
            "description": "A test category",
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.CREATED

    def test_create_category_as_regular_user(self, client, auth_headers):
        response = client.post("/categories/", headers=auth_headers, json={
            "title": "Forbidden Category",
            "description": "Should not work",
        })
        assert response.status_code == HTTPStatus.FORBIDDEN


class TestHealthEndpoints:
    def test_app_health(self, client):
        response = client.get("/health")
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["data"]["status"] == "healthy"

    def test_metrics_endpoint(self, client):
        response = client.get("/metrics")
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["success"] is True
