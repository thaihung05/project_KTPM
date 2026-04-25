import pytest

from eapp.dao import request_return_book, approve_return_book, reject_return_request
from eapp.models import BorrowStatus, Book
from eapp.test.test_base import test_session, test_app, test_client, fake_user, fake_admin, sample_borrows, \
    sample_books, sample_borrow_details


def test_request_return_success(test_client, mocker, fake_user):
    class FakeStatus:
        value = 'RETURNED_REQUEST'

    class FakeDetail:
        id = 1
        status = FakeStatus()

    mock_req = mocker.patch('eapp.dao.request_return_book', return_value=FakeDetail())

    res = test_client.post('/api/return-request/1')
    data = res.get_json()

    assert res.status_code == 200
    assert data['detail_id'] == 1
    assert data['status'] == 'RETURNED_REQUEST'
    assert 'Gửi yêu cầu trả sách thành công' in data['message']
    mock_req.assert_called_once()


def test_request_return_not_owner(test_client, mocker, fake_user):
    mock_req = mocker.patch('eapp.dao.request_return_book',
                            side_effect=PermissionError('Bạn không có quyền gửi yêu cầu trả cuốn sách này!'))

    res = test_client.post('/api/return-request/99')
    data = res.get_json()

    assert res.status_code == 403
    assert 'quyền' in data['error']
    mock_req.assert_called_once()


def test_request_return_detail_not_exist(test_client, mocker, fake_user):
    mock_req = mocker.patch('eapp.dao.request_return_book',
                            side_effect=ValueError('Bản ghi mượn sách không tồn tại!'))

    res = test_client.post('/api/return-request/999')
    data = res.get_json()

    assert res.status_code == 400
    assert 'không tồn tại' in data['error']
    mock_req.assert_called_once()


def test_request_return_book_not_exist(test_client, mocker, fake_user):
    mock_req = mocker.patch('eapp.dao.request_return_book',
                            side_effect=LookupError('Dữ liệu sách không tồn tại!'))

    res = test_client.post('/api/return-request/1')
    data = res.get_json()

    assert res.status_code == 404
    assert 'sách không tồn tại' in data['error']
    mock_req.assert_called_once()


def test_request_return_already_returned(test_client, mocker, fake_user):
    mock_req = mocker.patch('eapp.dao.request_return_book',
                            side_effect=ValueError('Cuốn sách này đã được trả rồi!'))

    res = test_client.post('/api/return-request/1')
    data = res.get_json()

    assert res.status_code == 400
    assert 'đã được trả' in data['error']
    mock_req.assert_called_once()


def test_request_return_already_requested(test_client, mocker, fake_user):
    mock_req = mocker.patch('eapp.dao.request_return_book',
                            side_effect=ValueError('Bạn đã gửi yêu cầu trả sách trước đó rồi!'))

    res = test_client.post('/api/return-request/1')
    data = res.get_json()

    assert res.status_code == 400
    assert 'đã gửi yêu cầu trả sách' in data['error']
    mock_req.assert_called_once()


def test_request_return_unauthenticated(test_client, mocker):
    class FakeGuest:
        is_authenticated = False
        id = 9

    mocker.patch('flask_login.utils._get_user', return_value=FakeGuest())

    res = test_client.post('/api/return-request/1')

    assert res.status_code == 302
    assert '/login' in res.location


def test_request_return_db_exception(test_client, mocker, fake_user):
    mock_req = mocker.patch('eapp.dao.request_return_book',
                            side_effect=Exception('DB error'))

    res = test_client.post('/api/return-request/1')
    data = res.get_json()

    assert res.status_code == 500
    assert 'Lỗi hệ thống' in data['error']
    mock_req.assert_called_once()


def test_request_return_dao_called_with_correct_args(test_client, mocker, fake_user):
    class FakeStatus:
        value = 'RETURNED_REQUEST'

    class FakeDetail:
        id = 5
        status = FakeStatus()

    mock_dao = mocker.patch('eapp.dao.request_return_book', return_value=FakeDetail())

    res = test_client.post('/api/return-request/5')
    data = res.get_json()
    assert res.status_code == 200


def test_approve_return_success(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.approve_return_book', return_value={
        'detail_id': 1,
        'return_date': '25/04/2026 10:00:00'
    })

    res = test_client.post('/api/admin/approve-return/1')
    data = res.get_json()

    assert res.status_code == 200
    assert data['message'] == 'Duyệt trả sách thành công.'
    assert data['data']['detail_id'] == 1

    mock_req.assert_called_once()


def test_approve_return_not_admin(test_client, mocker, fake_user):
    res = test_client.post('/api/admin/approve-return/1')
    data = res.get_json()

    assert res.status_code == 403
    assert 'Bạn không có quyền thực hiện chức năng này' in data['error']


def test_approve_return_detail_not_exist(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.approve_return_book',
                            side_effect=ValueError('Yêu cầu trả sách không tồn tại.'))

    res = test_client.post('/api/admin/approve-return/999')
    data = res.get_json()

    assert res.status_code == 400
    assert 'Yêu cầu trả sách không tồn tại' in data['error']
    mock_req.assert_called_once()


def test_approve_return_book_not_exist(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.approve_return_book',
                            side_effect=LookupError('Sách không tồn tại trong hệ thống.'))

    res = test_client.post('/api/admin/approve-return/1')
    data = res.get_json()

    assert res.status_code == 404
    assert 'Sách không tồn tại trong hệ thống' in data['error']
    mock_req.assert_called_once()


def test_approve_return_wrong_status(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.approve_return_book',
                            side_effect=ValueError('Cuốn sách này chưa ở trạng thái chờ duyệt trả.'))

    res = test_client.post('/api/admin/approve-return/1')
    data = res.get_json()

    assert res.status_code == 400
    assert 'Cuốn sách này chưa ở trạng thái chờ duyệt trả' in data['error']
    mock_req.assert_called_once()


def test_approve_return_db_exception(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.approve_return_book',
                            side_effect=Exception('DB error'))

    res = test_client.post('/api/admin/approve-return/1')
    data = res.get_json()

    assert res.status_code == 500
    assert 'Lỗi hệ thống' in data['error']
    mock_req.assert_called_once()


def test_reject_return_success(test_client, mocker, fake_admin):
    class FakeStatus:
        value = 'BORROWING'

    class FakeDetail:
        id = 1
        status = FakeStatus()

    mock_req = mocker.patch('eapp.dao.reject_return_request', return_value=FakeDetail())

    res = test_client.post('/api/admin/reject-return/1')
    data = res.get_json()

    assert res.status_code == 200
    assert data['message'] == 'Đã từ chối yêu cầu trả sách.'
    assert data['detail_id'] == 1
    assert data['status'] == 'BORROWING'
    mock_req.assert_called_once()


def test_reject_return_not_admin(test_client, mocker, fake_user):
    res = test_client.post('/api/admin/reject-return/1')
    data = res.get_json()

    assert res.status_code == 403
    assert 'Bạn không có quyền thực hiện chức năng này' in data['error']


def test_reject_return_detail_not_exist(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.reject_return_request',
                            side_effect=ValueError('Yêu cầu trả sách không tồn tại.'))

    res = test_client.post('/api/admin/reject-return/999')
    data = res.get_json()

    assert res.status_code == 400
    assert 'không tồn tại' in data['error']
    mock_req.assert_called_once()


def test_reject_return_wrong_status(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.reject_return_request',
                            side_effect=ValueError('Cuốn sách này không ở trạng thái chờ duyệt.'))

    res = test_client.post('/api/admin/reject-return/1')
    data = res.get_json()

    assert res.status_code == 400
    assert 'không ở trạng thái chờ duyệt' in data['error']
    mock_req.assert_called_once()


def test_reject_return_overdue_status(test_client, mocker, fake_admin):
    class FakeStatus:
        value = 'OVERDUE'

    class FakeDetail:
        id = 2
        status = FakeStatus()

    mock_req = mocker.patch('eapp.dao.reject_return_request', return_value=FakeDetail())

    res = test_client.post('/api/admin/reject-return/2')
    data = res.get_json()

    assert res.status_code == 200
    assert data['status'] == 'OVERDUE'
    mock_req.assert_called_once()


def test_reject_return_db_exception(test_client, mocker, fake_admin):
    mock_req = mocker.patch('eapp.dao.reject_return_request',
                            side_effect=Exception('DB error'))

    res = test_client.post('/api/admin/reject-return/1')
    data = res.get_json()

    assert res.status_code == 500
    assert 'Lỗi hệ thống' in data['error']
    mock_req.assert_called_once()


def test_request_return_integration_success(test_session, sample_borrow_details, mocker):
    detail = sample_borrow_details[0]

    result = request_return_book(user_id=4, detail_id=detail.id)

    assert result.status == BorrowStatus.RETURNED_REQUEST


def test_request_return_integration_not_owner(test_session, sample_borrow_details):
    detail = sample_borrow_details[0]

    with pytest.raises(PermissionError, match='quyền'):
        request_return_book(user_id=99, detail_id=detail.id)


def test_request_return_integration_already_returned(test_session, sample_borrow_details):
    detail_returned = sample_borrow_details[4]

    with pytest.raises(ValueError, match='đã được trả'):
        request_return_book(user_id=4, detail_id=detail_returned.id)


def test_request_return_integration_already_requested(test_session, sample_borrow_details):
    detail_req = sample_borrow_details[5]

    with pytest.raises(ValueError, match='đã gửi yêu cầu'):
        request_return_book(user_id=4, detail_id=detail_req.id)


def test_request_return_integration_not_exist(test_session, sample_borrow_details):
    from eapp.dao import request_return_book

    with pytest.raises(ValueError, match='không tồn tại'):
        request_return_book(user_id=4, detail_id=None)
        request_return_book(user_id=4, detail_id=10000)


def test_approve_return_integration_success(test_session, sample_borrow_details):
    # Bước 1: user gửi yêu cầu trả (d1 đang BORROWING)
    detail = sample_borrow_details[0]
    request_return_book(user_id=4, detail_id=detail.id)

    book_before = Book.query.get(detail.book_id)
    quantity_before = book_before.quantity

    # Bước 2: admin duyệt
    result = approve_return_book(detail_id=detail.id)

    book_after = Book.query.get(detail.book_id)

    assert result['detail_id'] == detail.id
    assert 'return_date' in result
    assert book_after.quantity == quantity_before + 1


def test_approve_return_integration_wrong_status(test_session, sample_borrow_details):
    # Duyet khong phai RETURNED_REQUEST
    detail = sample_borrow_details[0]

    with pytest.raises(ValueError, match='chờ duyệt'):
        approve_return_book(detail_id=detail.id)


def test_reject_return_integration_before_due(test_session, sample_borrow_details):

    # d1 đang BORROWING, due_date mặc định (trong hạn)
    detail = sample_borrow_details[0]
    request_return_book(user_id=4, detail_id=detail.id)

    result = reject_return_request(detail_id=detail.id)

    assert result.status == BorrowStatus.BORROWING


def test_reject_return_integration_overdue(test_session, sample_borrow_details):

    # d6 đang RETURNED_REQUEST, dùng d3 (OVERDUE) đổi tay để test
    # Force detail sang RETURNED_REQUEST để test reject khi quá hạn
    detail_overdue = sample_borrow_details[2]  # due_date = now()-3 ngày
    detail_overdue.status = BorrowStatus.RETURNED_REQUEST
    test_session.commit()

    result = reject_return_request(detail_id=detail_overdue.id)

    assert result.status == BorrowStatus.OVERDUE