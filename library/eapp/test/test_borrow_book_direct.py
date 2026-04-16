from eapp.test.test_base import test_app, test_client, fake_user

def test_api_borrow_direct_success(test_client, mocker, fake_user):
    class FakeBook1:
        id = 1
        title = "Sách Python"
        quantity = 5

    class FakeBook2:
        id = 2
        title = "Sách Java"
        quantity = 10

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)



    def get_book_logic(book_id):
        if book_id == 1:
            return FakeBook1()
        if book_id == 2:
            return FakeBook2()
        return None

    mocker.patch('eapp.dao.get_book_by_id', side_effect=get_book_logic)
    mock_add = mocker.patch('eapp.dao.add_borrow_record', return_value=True)

    res = test_client.post('/api/borrow/2')
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == 200
    assert "Mượn thành công" in data["message"]

    mock_add.assert_called_once_with(4,2)


def test_api_borrow_fail_not_found(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)

    mocker.patch('eapp.dao.get_book_by_id', return_value=None)

    res = test_client.post('/api/borrow/999')
    data = res.get_json()

    assert res.status_code == 404
    assert data["status"] == 404
    assert "không tồn tại" in data["message"]


def test_api_borrow_fail_account_locked(test_client, mocker):
    class FakeUser:
        id = 4
        active = False
        is_authenticated = True

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 403
    assert data["status"] == 403
    assert "bị khóa" in data["message"]

def test_api_borrow_fail_limit_exceeded(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=5)

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 400
    assert data["status"] == 400
    assert "tối đa 5 quyển" in data["message"]

def test_api_borrow_fail_overdue_books(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=True)

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 400
    assert data["status"] == 400
    assert "quá hạn chưa trả" in data["message"]

def test_api_borrow_fail_out_of_stock(test_client, mocker, fake_user):
    class FakeBook:
        id = 1
        title = "Sách Python"
        quantity = 0

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 400
    assert data["status"] == 400
    assert "hết hàng" in data["message"] or "không còn" in data["message"]


def test_api_borrow_fail_unauthorized(test_client, mocker):
    class FakeGuest:
        is_authenticated = False

    mocker.patch('flask_login.utils._get_user', return_value=FakeGuest())

    res = test_client.post('/api/borrow/1')

    assert res.status_code == 302
    assert "/login" in res.location


def test_api_borrow_fail_database_error(test_client, mocker, fake_user):
    class FakeBook:
        id = 1
        title = "Sách Python"
        quantity = 5
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    mock_add = mocker.patch('eapp.dao.add_borrow_record', return_value=False)

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 500
    assert data["status"] == 500
    assert data["message"] == "Hệ thống gặp lỗi!!"

    mock_add.assert_called_once_with(4,1)

def test_api_borrow_boundary_quantity_1(test_client, mocker, fake_user):
    class FakeBook:
        id = 1
        title = "Sách Python"
        quantity = 1

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    mock_add = mocker.patch('eapp.dao.add_borrow_record', return_value=True)

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert data["status"] == 200
    assert res.status_code == 200
    assert data["new_quantity"] == 1
    assert 'Mượn thành công' in data['message']

    mock_add.assert_called_once_with(4, 1)

def test_api_borrow_no_dao_called_when_account_is_locked(test_client, mocker):
    class FakeUser:
        id=4
        active = False
        is_authenticated = True

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mock_active_book = mocker.patch('eapp.dao.count_active_books')
    mock_add = mocker.patch('eapp.dao.add_borrow_record')

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert data["status"] == 403

    mock_active_book.assert_not_called()
    mock_add.assert_not_called()

def test_api_borrow_book_skip_overdue_when_borrow_over_5_book(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=5)
    mock_overdue_book = mocker.patch('eapp.dao.has_overdue_books')

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert data["status"] == 400
    assert data['status'] == 400
    mock_overdue_book.assert_not_called()
def test_api_borrow_skip_get_book_when_overdue(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=True)

    mock_get_book = mocker.patch('eapp.dao.get_book_by_id')

    res = test_client.post('/api/borrow/1')

    assert res.status_code == 400
    mock_get_book.assert_not_called()
def test_api_borrow_book_quantity_none(test_client, mocker, fake_user):
    class FakeBook:
        id = 1
        title = 'Sách Python'
        quantity = None

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 500
    assert data["status"] == 500
def test_api_borrow_book_quantity_string(test_client, mocker, fake_user):
    class FakeBook:
        id = 1
        title = 'Sách Python'
        quantity = '1as'

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 500
    assert data["status"] == 500
def test_api_borrow_book_quantity_negative(test_client, mocker, fake_user):

    class FakeBook:
        id = 1
        title = 'Sách Python'
        quantity =  -2

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    res = test_client.post('/api/borrow/1')
    data = res.get_json()

    assert res.status_code == 500
    assert data["status"] == 500

def test_api_borrow_db_exception(test_client, mocker, fake_user):

    class FakeBook:
        id = 1
        title = "Sách Python"
        quantity = 5

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.get_book_by_id', return_value=FakeBook())

    mocker.patch('eapp.dao.add_borrow_record', side_effect=Exception("DB error"))

    res = test_client.post('/api/borrow/1')
    data = res.get_json()
    assert res.status_code == 500
    assert data["status"] == 500

