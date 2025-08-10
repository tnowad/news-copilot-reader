import pytest
from app import create_app
from app.extensions import db as _db
from app.models.role import Role, RoleEnum
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    _app = create_app("testing")
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    _db.create_all()

    for role in RoleEnum:
        r = Role(name=role)
        _db.session.add(r)
    _db.session.commit()

    yield _db

    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.create_scoped_session(options={"bind": connection, "binds": {}})
    db.session = session
    db.session.begin_nested()

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app, session):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client, session):
    user = User(
        email="testuser@example.com",
        display_name="Test User",
    )
    user.set_password("TestPass123!")
    user_role = Role.query.filter_by(name=RoleEnum.USER).first()
    if user_role:
        user.roles.append(user_role)
    session.add(user)
    session.commit()

    response = client.post("/auth/sign-in", json={
        "email": "testuser@example.com",
        "password": "TestPass123!",
    })
    data = response.get_json()
    token = data["data"]["token"]["accessToken"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, session):
    user = User(
        email="admin@example.com",
        display_name="Admin User",
    )
    user.set_password("AdminPass123!")
    admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
    user_role = Role.query.filter_by(name=RoleEnum.USER).first()
    if admin_role:
        user.roles.append(admin_role)
    if user_role:
        user.roles.append(user_role)
    session.add(user)
    session.commit()

    response = client.post("/auth/sign-in", json={
        "email": "admin@example.com",
        "password": "AdminPass123!",
    })
    data = response.get_json()
    token = data["data"]["token"]["accessToken"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user(session):
    user = User(
        email="sample@example.com",
        display_name="Sample User",
    )
    user.set_password("SamplePass123!")
    user_role = Role.query.filter_by(name=RoleEnum.USER).first()
    if user_role:
        user.roles.append(user_role)
    session.add(user)
    session.commit()
    return user
