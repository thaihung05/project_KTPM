import math
from datetime import date, datetime, timedelta

import pytest

from eapp.dao import request_return_book, approve_return_book, reject_return_request, update_overdue_status
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
    assert 'không có quyền' in data['error']
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
        'return_date': '25/04/2026 10:00:00',
        'status': BorrowStatus.RETURNED.name
    })

    res = test_client.post('/api/admin/approve-return/1')
    data = res.get_json()
    print(data)
    assert res.status_code == 200
    assert data['message'] == 'Duyệt trả sách thành công.'
    assert data['data']['detail_id'] == 1
    assert data['data']['return_date'] != None
    assert data['data']['status'] == BorrowStatus.RETURNED.name

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


def test_approve_return_unauthenticated(test_client, mocker):
    class FakeGuest:
        is_authenticated = False

    mocker.patch('flask_login.utils._get_user', return_value=FakeGuest())

    res = test_client.post('/api/admin/approve-return/1')
    assert res.status_code == 302
    assert '/login' in res.location


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


def test_approve_return_integration_success(test_session, sample_borrow_details):
    detail = sample_borrow_details[0]
    request_return_book(user_id=4, detail_id=detail.id)

    book_before = Book.query.get(detail.book_id)
    quantity_before = book_before.quantity

    result = approve_return_book(detail_id=detail.id)

    book_after = Book.query.get(detail.book_id)

    assert result['detail_id'] == detail.id
    assert 'return_date' in result
    assert book_after.quantity == quantity_before + 1


def test_approve_return_integration_wrong_status(test_session, sample_borrow_details):
    detail = sample_borrow_details[0]

    with pytest.raises(ValueError, match='chờ duyệt'):
        approve_return_book(detail_id=detail.id)


def test_approve_return_integration_book_available_restored(test_session, sample_borrow_details):
    detail = sample_borrow_details[0]
    request_return_book(user_id=4, detail_id=detail.id)

    book = Book.query.get(detail.book_id)
    book.quantity = 0
    book.available = False
    test_session.commit()

    approve_return_book(detail_id=detail.id)

    book_after = Book.query.get(detail.book_id)
    assert book_after.quantity == 1
    assert book_after.available is True


def test_reject_return_integration_before_due(test_session, sample_borrow_details):
    detail = sample_borrow_details[0]
    request_return_book(user_id=4, detail_id=detail.id)

    result = reject_return_request(detail_id=detail.id)

    assert result.status == BorrowStatus.BORROWING


def test_reject_return_integration_overdue(test_session, sample_borrow_details):
    detail_overdue = sample_borrow_details[2]
    detail_overdue.status = BorrowStatus.RETURNED_REQUEST
    test_session.commit()

    result = reject_return_request(detail_id=detail_overdue.id)

    assert result.status == BorrowStatus.OVERDUE


def test_db_error_rollback(test_session, mocker, sample_borrow_details):
    mocker.patch('eapp.dao.db.session.commit', side_effect=Exception('DB failure'))
    mock_rollback = mocker.patch('eapp.dao.db.session.rollback')

    with pytest.raises(Exception):
        update_overdue_status()

    mock_rollback.assert_called_once()


def test_borrowing_not_due_unchanged(test_session, sample_borrow_details):
    update_overdue_status()

    d1 = sample_borrow_details[0]

    test_session.refresh(d1)

    assert d1.status == BorrowStatus.BORROWING
    assert d1.fine == 0


def test_overdue_fine_recalculated(test_session, sample_borrow_details):
    update_overdue_status()

    d3 = sample_borrow_details[2]
    test_session.refresh(d3)

    late_seconds = (datetime.now() - d3.due_date).total_seconds()
    expected_days = math.ceil(late_seconds / 86400)
    expected_fine = expected_days * 5000
    assert d3.status == BorrowStatus.OVERDUE
    assert d3.fine == expected_fine


def test_overdue_status_stays_overdue(test_session, sample_borrow_details):
    update_overdue_status()

    d3 = sample_borrow_details[2]
    d4 = sample_borrow_details[3]
    test_session.refresh(d3)
    test_session.refresh(d4)

    assert d3.status == BorrowStatus.OVERDUE
    assert d4.status == BorrowStatus.OVERDUE


def test_borrowing_to_overdue_when_past_due(test_session, sample_borrow_details):
    d1 = sample_borrow_details[0]
    d1.due_date = datetime.now() - timedelta(days=5, seconds=1)
    test_session.commit()

    update_overdue_status()

    test_session.refresh(d1)
    assert d1.status == BorrowStatus.OVERDUE
    assert d1.fine == 6 * 5000


def test_fine_boundary_one_day(test_session, sample_borrow_details):
    d2 = sample_borrow_details[1]
    d2.due_date = datetime.now() - timedelta(days=1, seconds=1)
    test_session.commit()

    update_overdue_status()

    test_session.refresh(d2)
    assert d2.status == BorrowStatus.OVERDUE
    assert d2.fine == 2 * 5000


def test_due_today_not_overdue(test_session, sample_borrow_details):
    d1 = sample_borrow_details[0]
    d1.due_date = datetime.combine(date.today(), datetime.max.time())
    test_session.commit()

    update_overdue_status()

    test_session.refresh(d1)
    assert d1.status == BorrowStatus.BORROWING
    assert d1.fine == 0


def test_multiple_calls(test_session, sample_borrow_details):
    update_overdue_status()
    update_overdue_status()
    update_overdue_status()

    d3 = sample_borrow_details[2]
    test_session.refresh(d3)

    now = datetime.now()
    late_seconds = (now - d3.due_date).total_seconds()
    expected_days = math.ceil(late_seconds / 86400)
    expected_fine = expected_days * 5000

    assert d3.fine == expected_fine


def test_returned_record_not_touched(test_session, sample_borrow_details):
    update_overdue_status()

    d5 = sample_borrow_details[4]
    test_session.refresh(d5)

    assert d5.status == BorrowStatus.RETURNED
    assert d5.fine == 0


def test_returned_request_fine_frozen(test_session, sample_borrow_details):
    d6 = sample_borrow_details[5]
    d6.due_date = datetime.now() - timedelta(days=5)
    test_session.commit()

    update_overdue_status()

    test_session.refresh(d6)
    assert d6.status == BorrowStatus.RETURNED_REQUEST
    assert d6.fine == 0


def test_admin_approve_request_view_forbidden_for_user(test_client, fake_user):
    res = test_client.get('/admin/approve_request_view')
    assert res.status_code == 302
    assert '/books' in res.location


def test_admin_approve_request_view_accessible_for_admin(test_client, fake_admin, mocker):
    mocker.patch('eapp.dao.get_return_requests', return_value=[])
    res = test_client.get('/admin/approve_request_view')
    assert res.status_code == 200


def test_admin_approve_request_view_unauthenticated(test_client):
    res = test_client.get('/admin/approve_request_view')
    assert res.status_code == 302
    assert '/login' in res.location