from datetime import datetime, timedelta
import pytest
from eapp.dao import load_borrowed_books, load_borrowing_books, load_all_borrowed_books
from eapp.models import BorrowDetails, BorrowStatus
from eapp.test.test_base import test_client, test_app, test_session, sample_borrows, sample_books, \
    sample_borrow_details, fake_user


def test_load_all_borrowed_books_success(sample_borrow_details):
    all_books = load_all_borrowed_books(user_id=4)
    assert len(all_books) == len(sample_borrow_details)

    count_books_overdue = 0
    count_books_borrowing = 0
    count_books_borrowed = 0
    count_books_return_req = 0

    for details, borrow, books in all_books:
        assert borrow.user_id == 4
        assert details.borrow_id == borrow.id
        assert details.book_id == books.id
        if details.status == BorrowStatus.BORROWING:
            count_books_borrowing += 1
        elif details.status == BorrowStatus.OVERDUE:
            count_books_overdue += 1
        elif details.status == BorrowStatus.RETURNED_REQUEST:
            count_books_return_req+=1
        else:
            count_books_borrowed+=1

    assert count_books_return_req==1
    assert count_books_overdue==2
    assert count_books_borrowing==2
    assert count_books_borrowed==1

def test_load_all_borrowed_books_empty(sample_borrow_details):
    all_books = load_all_borrowed_books(user_id=3)
    assert len(all_books) == 0


def test_load_borrowed_book_success(sample_borrow_details):
    actual_borrowed_books = load_borrowed_books(user_id=4)

    assert len(actual_borrowed_books) == 1

    for details, borrow, books in actual_borrowed_books:
        assert borrow.user_id == 4
        assert details.return_date is not None
        assert details.status == BorrowStatus.RETURNED


def test_load_borrowed_book_empty(sample_borrow_details):
    borrowed_books = load_borrowed_books(user_id=3)
    assert len(borrowed_books) == 0


def test_load_borrowing_books(sample_borrow_details):
    borrowing_books = load_borrowing_books(user_id=4)
    assert len(borrowing_books) == 5

    for details, borrow, books in borrowing_books:
        assert borrow.user_id == 4
        assert details.return_date is None
        assert details.status != BorrowStatus.RETURNED


def test_load_borrowing_books_empty(sample_borrow_details):
    borrowing_books = load_borrowing_books(user_id=3)
    assert len(borrowing_books) == 0


def test_my_books_consistency(sample_borrow_details):
    all_books = load_all_borrowed_books(user_id=4)
    borrowed_books = load_borrowed_books(user_id=4)
    borrowing_books = load_borrowing_books(user_id=4)

    assert len(all_books) == len(sample_borrow_details)
    assert len(borrowed_books) == 1
    assert len(borrowing_books) == 5
    assert len(borrowed_books) + len(borrowing_books) == len(all_books)


def test_route_my_books_list_success(test_client, fake_user, mocker):
    class FakeDetail:
        borrowed_date=datetime.now()
        due_date=datetime.now()+timedelta(days=14)
        return_date = datetime.now()+timedelta(days=3)
        status = BorrowStatus.RETURNED
        fine = 0

    class FakeBorrow:
        user_id=4
        create_date=datetime.now()

    class FakeBook:
        id = 1
        title = 'Sách Python'
        quantity =  2

    fake_books = [(FakeDetail(),FakeBorrow(),FakeBook())]
    mock_load=mocker.patch("eapp.dao.load_all_borrowed_books", return_value=fake_books)
    res= test_client.get('/my_books_list')

    assert res.status_code==200
    mock_load.assert_called_once()


def test_route_my_books_list_empty(test_client, fake_user, mocker):
    fake_books = []
    mock_load=mocker.patch("eapp.dao.load_all_borrowed_books", return_value=fake_books)
    res= test_client.get('/my_books_list')

    assert res.status_code==200
    assert 'Chưa có sách!'.encode() in res.data
    mock_load.assert_called_once()



def test_route_my_books_list_require_login(test_client):
    res= test_client.get('/my_books_list')
    assert res.status_code==302


def test_route_my_borrowed_books_success(test_client, fake_user, mocker):
    class FakeDetail:
        borrowed_date=datetime.now()
        due_date=datetime.now()+timedelta(days=14)
        return_date = datetime.now()+timedelta(days=3)
        status = BorrowStatus.RETURNED
        fine = 0

    class FakeBorrow:
        user_id=4
        create_date=datetime.now()

    class FakeBook:
        id = 1
        title = 'Sách Python'
        quantity =  2

    fake_books = [(FakeDetail(),FakeBorrow(),FakeBook())]
    mock_load=mocker.patch("eapp.dao.load_borrowed_books", return_value=fake_books)
    res= test_client.get('/my_borrowed_books')

    assert res.status_code==200
    mock_load.assert_called_once()


def test_route_my_borrowed_books_empty(test_client, fake_user, mocker):
    fake_books = []
    mock_load=mocker.patch("eapp.dao.load_borrowed_books", return_value=fake_books)
    res= test_client.get('/my_borrowed_books')

    assert res.status_code==200
    assert 'Chưa có sách đã mượn!'.encode() in res.data
    mock_load.assert_called_once()

def test_route_my_borrowed_books_require_login(test_client):
    res= test_client.get('/my_borrowed_books')
    assert res.status_code==302


def test_route_my_borrowing_books_success(test_client, fake_user, mocker):
    class FakeDetail:
        borrowed_date=datetime.now()
        due_date=datetime.now()+timedelta(days=14)
        status = BorrowStatus.BORROWING
        fine = 0

    class FakeBorrow:
        user_id=4
        create_date=datetime.now()

    class FakeBook:
        id = 1
        title = 'Sách Python'
        quantity =  2

    fake_books = [(FakeDetail(),FakeBorrow(),FakeBook())]
    mock_load=mocker.patch("eapp.dao.load_borrowing_books", return_value=fake_books)
    res= test_client.get('/my_borrowing_books')

    assert res.status_code==200
    mock_load.assert_called_once()


def test_route_my_borrowing_books_empty(test_client, fake_user, mocker):
    fake_books = []
    mock_load=mocker.patch("eapp.dao.load_borrowing_books", return_value=fake_books)
    res= test_client.get('/my_borrowing_books')

    assert res.status_code==200
    assert 'Chưa có sách đang mượn!'.encode() in res.data
    mock_load.assert_called_once()


def test_route_my_borrowing_books_require_login(test_client):
    res= test_client.get('/my_borrowing_books')
    assert res.status_code==302



def test_route_my_books_list_db_error(test_client, fake_user, mocker):
    mocker.patch("eapp.dao.load_all_borrowed_books", side_effect=Exception("DB error"))
    res = test_client.get('/my_books_list')
    assert res.status_code == 500


def test_route_my_borrowed_books_db_error(test_client, fake_user, mocker):
    mocker.patch("eapp.dao.load_borrowed_books", side_effect=Exception("DB error"))
    res = test_client.get('/my_borrowed_books')
    assert res.status_code == 500


def test_route_my_borrowing_books_db_error(test_client, fake_user, mocker):
    mocker.patch("eapp.dao.load_borrowing_books", side_effect=Exception("DB error"))
    res = test_client.get('/my_borrowing_books')
    assert res.status_code == 500

def test_route_my_books_list_failed_authenticated(test_client,mocker):
    class FakeUser:
        is_authenticated=False

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    res = test_client.get('/my_books_list')
    assert res.status_code == 302

    res = test_client.get('/my_borrowed_books')
    assert res.status_code == 302

def test_route_my_borrowing_books_failed_authenticated(test_client,mocker):
    class FakeUser:
        is_authenticated=False

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    res = test_client.get('/my_borrowing_books')
    assert res.status_code==302


def test_route_my_borrowed_books_failed_authenticated(test_client,mocker):
    class FakeUser:
        is_authenticated=False

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    res = test_client.get('/my_borrowed_books')
    assert res.status_code == 302







