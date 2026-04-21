import pytest
from flask import Flask
from eapp import db, login
from eapp.index import register_routes
from eapp.models import UserRole, Book, Category


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

@pytest.fixture()
def sample_books(test_session):
    c1 = Category(id=1, name="CNTT")
    c2 = Category(id=2, name="Văn học")
    test_session.add_all([c1, c2])
    test_session.commit()

    b1 = Book(title="Lập trình Python cơ bản", author="Trần Văn A", quantity=10, category_id=1, available=True)
    b2 = Book(title="Python nâng cao và chuyên sâu", author="Nguyễn Thị B", quantity=8, category_id=1, available=True)
    b3 = Book(title="Java cơ bản cho người mới", author="Trần Văn A", quantity=5, category_id=1, available=True)
    b4 = Book(title="Dế Mèn phiêu lưu ký", author="Tô Hoài", quantity=7, category_id=2, available=True)
    b5 = Book(title="Lập trình hướng đối tượng với Python", author="Nguyễn Văn C", quantity=6, category_id=1, available=True)
    b6 = Book(title="Truyện Kiều - Nguyễn Du", author="Nguyễn Du", quantity=5, category_id=2, available=True)
    b7 = Book(title="Chí Phèo - Nam Cao", author="Nam Cao", quantity=4, category_id=2, available=True)
    b8 = Book(title="Số đỏ - Vũ Trọng Phụng", author="Vũ Trọng Phụng", quantity=3, category_id=2, available=True)

    test_session.add_all([b1, b2, b3, b4, b5, b6, b7, b8])
    test_session.commit()

    return [b1, b2, b3, b4, b5, b6, b7, b8]