from eapp.test.test_base import test_app, test_client, fake_user

def test_register_success(test_client, mocker):
    mocker.patch('eapp.dao.register', return_value=None)
    res = test_client.post('/register', data={
        'username': 'Roy',
        'password': '123',
        'confirm': '123',
        'name': 'Huy'
    })

    assert res.status_code == 302
    assert '/login' in res.location

def test_register_password_not_match(test_client):
    res = test_client.post('/register', data={
        'username': 'roy',
        'password': '123',
        'confirm': '456',
        'name': 'Huy'
    })

    assert res.status_code == 200
    assert "Mật khẩu không khớp" in res.get_data(as_text=True)
def test_register_username_exist(test_client, mocker):
    mocker.patch('eapp.index.register', side_effect=Exception("Username đã tồn tại!!"))
    mocker.patch('eapp.index.render_template', return_value="Username này đã được đăng ký!!")

    res = test_client.post('/register', data={
        'username': 'Roy',
        'password': '123',
        'confirm': '123',
        'name': 'Huy'
    })

    assert res.status_code == 200
    assert "Username này đã được đăng ký" in res.get_data(as_text=True)

def test_login_success(test_client, mocker):
    class FakeUser:
        id = 1
        is_active = True
        def get_id(self):
            return str(self.id)

    mocker.patch('eapp.dao.auth_user', return_value=FakeUser())
    mocker.patch('flask_login.utils.login_user', return_value=True)
    res = test_client.post('/login', data={
        'username': 'huy01',
        'password': '123'
    })

    assert res.status_code == 302

def test_login_fail(test_client, mocker):
    mocker.patch('eapp.dao.auth_user', return_value=None)

    res = test_client.post('/login', data={
        'username': 'huy01',
        'password': '123'
    })

    assert res.status_code == 200
    assert "không chính xác" in res.get_data(as_text=True)

def test_login_sets_session(test_client, mocker):
    class FakeUser:
        id = 1
        is_active = True
        def get_id(self):
            return str(self.id)

    mocker.patch('eapp.dao.auth_user', return_value=FakeUser())

    test_client.post('/login', data={
        'username': 'huy01',
        'password': '123'
    })

    with test_client.session_transaction() as sess:
        assert '_user_id' in sess

def test_logout_when_logged_in(test_client, mocker):
    class FakeUser:
        id = 1
        is_active = True
        def get_id(self):
            return str(self.id)

    mocker.patch('eapp.dao.auth_user', return_value=FakeUser())

    test_client.post('/login', data={
        'username': 'huy01',
        'password': '123'
    })

    res = test_client.get('/logout')
    assert res.status_code == 302

    with test_client.session_transaction() as sess:
        assert '_user_id' not in sess

def test_logout_without_login(test_client):
    res = test_client.get('/logout')
    assert res.status_code == 302

def test_login_missing_field(test_client, mocker):
    mocker.patch('eapp.dao.auth_user', return_value=None)

    res = test_client.post('/login', data={
        'username': 'huy01'
    })

    assert res.status_code == 200
    assert 'Vui lòng nhập đầy đủ' in res.get_data(as_text=True)

def test_register_missing_field(test_client):
    res = test_client.post('/register', data={
        'username': 'roy'
    })
    assert res.status_code == 200
    assert "Vui lòng điền đầy đủ" in res.get_data(as_text=True)

def test_cart_redirect_to_login_with_next(test_client):
    res = test_client.get('/cart')

    assert res.status_code == 302
    assert '/login' in res.location
    assert 'next=%2Fcart' in res.location

def test_login_redirect_back_to_cart(test_client, mocker):
    class FakeUser:
        id = 1
        is_active = True
        def get_id(self):
            return str(self.id)

    mocker.patch('eapp.dao.auth_user', return_value=FakeUser())

    mocker.patch('flask_login.utils.login_user', return_value=True)

    res = test_client.post('/login?next=/cart', data={
        'username': 'huy01',
        'password': '123'
    })

    assert res.status_code == 302
    assert '/cart' in res.location

def test_login_without_next_redirect_home(test_client, mocker):
    class FakeUser:
        id = 1
        is_active = True
        def get_id(self):
            return str(self.id)

    mocker.patch('eapp.dao.auth_user', return_value=FakeUser())

    res = test_client.post('/login', data={
        'username': 'huy01',
        'password': '123'
    })

    assert res.status_code == 302
    assert "/" in res.location
