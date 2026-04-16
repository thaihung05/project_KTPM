import pytest
from flask import Flask
from eapp import db, login
from eapp.index import register_routes
from eapp.models import UserRole


def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.secret_key = "passwordAbc123"
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
    app.config["PAGE_SIZE"] = 25
    app.config["TESTING"] = True
    app.config["LOGIN_DISABLED"] = False
    login.init_app(app)
    db.init_app(app)
    register_routes(app)
    return app

@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def fake_user(test_app, mocker):
    class FakeUser:
        id = 4
        is_authenticated = True
        active=True
        user_role = UserRole.USER

    mocker.patch('flask_login.utils._get_user', new=FakeUser)
