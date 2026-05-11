import os
from datetime import datetime, timedelta

import pytest
from flask import Flask
from selenium.webdriver.chrome.service import Service

from eapp import db, login
from eapp.index import register_routes
from eapp.models import UserRole, Book, Category, Borrow, BorrowDetails, BorrowStatus
from selenium import webdriver


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

    @app.context_processor
    def mock_context_processor():
        return {
            'cart_stats': {
                'total_quantity': 0
            }
        }

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
        active = True
        user_role = UserRole.USER

    mocker.patch('flask_login.utils._get_user', new=FakeUser)


@pytest.fixture
def fake_admin(test_app, mocker):
    class FakeAdmin:
        id = 1
        is_authenticated = True
        active = True
        user_role = UserRole.ADMIN

    mocker.patch('flask_login.utils._get_user', return_value=FakeAdmin())


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
    b5 = Book(title="Lập trình hướng đối tượng với Python", author="Nguyễn Văn C", quantity=6, category_id=1,
              available=True)
    b6 = Book(title="Truyện Kiều - Nguyễn Du", author="Nguyễn Du", quantity=5, category_id=2, available=True)
    b7 = Book(title="Chí Phèo - Nam Cao", author="Nam Cao", quantity=4, category_id=2, available=True)
    b8 = Book(title="Số đỏ - Vũ Trọng Phụng", author="Vũ Trọng Phụng", quantity=3, category_id=2, available=True)

    test_session.add_all([b1, b2, b3, b4, b5, b6, b7, b8])
    test_session.commit()
    return [b1, b2, b3, b4, b5, b6, b7, b8]


@pytest.fixture
def sample_borrows(test_session):
    user_id = 4
    br1 = Borrow(user_id=user_id)
    br2 = Borrow(user_id=user_id)
    br3 = Borrow(user_id=user_id)
    br4 = Borrow(user_id=user_id)
    br5 = Borrow(user_id=user_id)
    br6 = Borrow(user_id=user_id)

    borrows = [br1, br2, br3, br4, br5, br6]

    db.session.add_all(borrows)
    db.session.commit()
    return borrows


@pytest.fixture
def sample_borrow_details(test_session, sample_borrows, sample_books):
    d1 = BorrowDetails(borrow_id=sample_borrows[0].id, book_id=sample_books[0].id)
    d2 = BorrowDetails(borrow_id=sample_borrows[1].id, book_id=sample_books[1].id)
    d3 = BorrowDetails(borrow_id=sample_borrows[2].id, book_id=sample_books[2].id,
                       due_date=datetime.now() - timedelta(days=3),
                       status=BorrowStatus.OVERDUE, fine=15000)
    d4 = BorrowDetails(borrow_id=sample_borrows[3].id, book_id=sample_books[3].id,
                       due_date=datetime.now() - timedelta(days=3), status=BorrowStatus.OVERDUE, fine=15000)
    d5 = BorrowDetails(borrow_id=sample_borrows[4].id, book_id=sample_books[4].id,
                       return_date=datetime.now() + timedelta(days=3), status=BorrowStatus.RETURNED)
    d6 = BorrowDetails(borrow_id=sample_borrows[5].id, book_id=sample_books[5].id, status=BorrowStatus.RETURNED_REQUEST)

    details = [d1, d2, d3, d4, d5, d6]
    db.session.add_all(details)
    db.session.commit()
    return details

@pytest.fixture
def driver():
    service = Service(executable_path='.venv/chromedriver')
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()