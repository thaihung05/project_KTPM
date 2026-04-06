from eapp.test.test_base import test_app, test_client

def test_request_success(test_client, mocker):
    class FakeUser:
        id=4
        is_authenticated = True

    class FakeStatus:
        value = 'RETURNED_REQUEST'
    class FakeBooks:
        id=1
        status=FakeStatus()

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())


    mock_request = mocker.patch('eapp.dao.request_return_book', return_value=FakeBooks())
    res = test_client.post('/api/return-request/1')
    data = res.get_json()

    assert res.status_code == 200
    assert data["detail_id"] == 1
    assert data["status"] == "RETURNED_REQUEST"
    mock_request.assert_called_once()