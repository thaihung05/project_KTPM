from eapp.test.test_base import test_app, test_client, fake_user

def test_add_to_cart(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {}

    res = test_client.post('/api/cart', json={
        'id' : 1,
        'title' : 'Sách Python',
        'quantity' : 1
    })

    data = res.get_json()


    assert res.status_code == 200
    assert data['total_quantity'] == 1



def test_existed_item_add_to_cart(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
        '1':{
            'id' : 1,
            'title': 'Sách Python',
            'quantity' : 1
            }
        }
    res = test_client.post('/api/cart', json={
        'id': 1,
        'title': 'Sách Python',
        'quantity': 1
    })

    data = res.get_json()


    assert res.status_code == 400
    assert 'Sách này đã có trong danh sách' in data['message']
    with test_client.session_transaction() as sess:
        assert 'cart' in sess
        assert len(sess['cart']) == 1
        assert sess['cart']['1']['quantity'] == 1



def test_delete_from_cart(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            '1': {
                'id': 1,
                'title': 'Sách Python',
                'quantity': 1
            }
        }

    res = test_client.delete('/api/cart/1')

    data = res.get_json()

    assert res.status_code == 200
    assert data['total_quantity'] == 0
    with test_client.session_transaction() as sess:
        assert 'cart' in sess
        assert len(sess['cart']) == 0

def test_deleta_not_found_id(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
            'id': 1,
            'title': 'Sách Python',
            'quantity': 1
            }
        }

    res = test_client.delete('/api/cart/2')
    data = res.get_json()

    assert res.status_code == 404

    assert 'Không tìm thấy sách' in data['message']

    with test_client.session_transaction() as sess:
        assert 'cart' in sess
        assert len(sess['cart']) == 1
        assert sess['cart']['1']['id'] == 1

def test_confirm_borrow_success(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                'id': 1,
                'title': 'Sách Python',
                'quantity': 1
            },
            "2": {
                'id': 2,
                'title': 'Sách Python 2',
                'quantity': 1
            }
        }

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.add_multi_borrow_record', return_value=(True, "OK"))

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1, 2]})

    assert res.status_code == 200
    data = res.get_json()
    with test_client.session_transaction() as sess:
        assert len(sess['cart']) == 0


def test_confirm_borrow_has_overdue(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=True)

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1]})
    data = res.get_json()

    assert data['status'] == 400
    assert 'quá hạn' in data['message']

def test_confirm_borrow_user_locked(test_client, mocker):
    class FakeUser:
        id = 1
        active = False
        is_authenticated = True
    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1]})
    data = res.get_json()
    assert data['status'] == 403
    assert "bị khóa" in data['message']

def test_confirm_borrow_limit_exceeded(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=4)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1,2,3]})
    data = res.get_json()
    assert data['status'] == 400
    assert 'chỉ được chọn thêm 1 quyển nữa thôi' in data['message']

def test_confirm_borrow_fail(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            '1': {
                'id': 1,
                'title': 'Sách Python',
                'quantity': 1
            }
        }

    mocker.patch('eapp.dao.add_multi_borrow_record',return_value=(False, "Sách đã hết"))

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1]})
    data = res.get_json()

    assert data['status'] == 500
    assert 'Sách đã hết' in data['message']

    with test_client.session_transaction() as sess:
        assert '1' in sess['cart']


def test_confirm_borrow_partial_clear_cart(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            '1':
                {
                    'id': 1,
                    'title': 'Sách Python',
                    'quantity': 1
                 },
            '2':
                {
                    'id': 2,
                    'title': 'Sách Python 2',
                    'quantity': 1
                }
        }

    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)
    mocker.patch('eapp.dao.add_multi_borrow_record', return_value=(True, "Mượn thành công"))

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1]})
    data = res.get_json()
    assert data['status'] == 200
    with test_client.session_transaction() as sess:
        assert '1' not in sess['cart']
        assert '2' in sess['cart']


def test_delete_empty_cart(test_client, mocker, fake_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {}
    res = test_client.delete('/api/cart/1')
    assert res.status_code == 404


def test_confirm_borrow_invalid_format(test_client, mocker, fake_user):
    res = test_client.post('/api/confirm-borrow', json={'book_ids': "sb"})
    data = res.get_json()
    assert res.status_code == 200
    assert data['status'] == 500

def test_confirm_borrow_unauthorized(test_client):
    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1]})
    assert res.status_code == 302


def test_confirm_borrow_book_not_exists_in_db(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=0)
    mocker.patch('eapp.dao.has_overdue_books', return_value=False)

    mocker.patch('eapp.dao.add_multi_borrow_record', return_value=(False, "Sách không tồn tại"))

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [999]})
    data = res.get_json()
    assert data['status'] == 500
    assert "Sách không tồn tại" in res.get_json()['message']


def test_confirm_borrow_at_limit_5(test_client, mocker, fake_user):
    mocker.patch('eapp.dao.count_active_books', return_value=5)

    res = test_client.post('/api/confirm-borrow', json={'book_ids': [1]})
    data = res.get_json()

    assert data['status'] == 400
    assert "chọn thêm 0 quyển" in data['message']


def test_delete_cart_unauthorized(test_client):
    res = test_client.delete('/api/cart/1')
    assert res.status_code == 302




