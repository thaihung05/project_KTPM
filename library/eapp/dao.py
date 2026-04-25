from datetime import date, datetime

from flask import Flask
from pymysql import IntegrityError

from eapp.models import Category, Book, UserRole, BorrowDetails, Borrow, BorrowStatus
from eapp import db, app
import hashlib
from eapp.models import User


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()


def load_categories():
    return Category.query.all()


def load_books(kw=None, search_by=None, cate_id=None, page=1, page_size=None):
    query = Book.query

    if kw:
        if search_by == 'author':
            query = query.filter(Book.author.contains(kw))
        elif search_by == 'title':
            query = query.filter(Book.title.contains(kw))

    if cate_id:
        query = query.filter(Book.category_id.__eq__(cate_id))

    if page:
        size = page_size if page_size else app.config.get('PAGE_SIZE')
        start = (page - 1) * size
        query = query.slice(start, start + size)

    return query.all()


def load_all_borrowed_books(user_id):
    update_overdue_status()

    query = (db.session.query(BorrowDetails, Borrow, Book)
             .join(Book, Book.id == BorrowDetails.book_id)
             .join(Borrow, Borrow.id == BorrowDetails.borrow_id)
             .filter(Borrow.user_id == user_id)
             .order_by(Borrow.create_date.desc())
             .all())

    return query


def load_borrowed_books(user_id):
    update_overdue_status()

    query = (db.session.query(BorrowDetails, Borrow, Book)
             .join(Book, Book.id == BorrowDetails.book_id)
             .join(Borrow, Borrow.id == BorrowDetails.borrow_id)
             .filter(Borrow.user_id == user_id, BorrowDetails.return_date != None)
             .order_by(Borrow.create_date.desc())
             .all())
    return query


def load_borrowing_books(user_id):
    update_overdue_status()

    query = (db.session.query(BorrowDetails, Borrow, Book)
             .join(Book, Book.id == BorrowDetails.book_id)
             .join(Borrow, Borrow.id == BorrowDetails.borrow_id)
             .filter(Borrow.user_id == user_id, BorrowDetails.return_date == None)
             .order_by(Borrow.create_date.desc())
             .all())
    return query


def count_books(kw=None, search_by=None, cate_id=None):
    query = Book.query
    if kw:
        if search_by == 'author':
            query = query.filter(Book.author.contains(kw))
        elif search_by == 'title':
            query = query.filter(Book.title.contains(kw))

    if cate_id:
        query = query.filter(Book.category_id.__eq__(cate_id))

    return query.count()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def register(username, password, name):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(username=username.strip(),
             password=password,
             name=name.strip(),
             user_role=UserRole.USER)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username đã tồn tại!')


def count_active_books(user_id):
    return db.session.query(BorrowDetails).join(Borrow).filter(
        Borrow.user_id == user_id,
        BorrowDetails.return_date == None
    ).count()


def has_overdue_books(user_id):
    active_details = db.session.query(BorrowDetails).join(Borrow).filter(
        Borrow.user_id == user_id,
        BorrowDetails.return_date == None
    ).all()
    return any(d.is_overdue() for d in active_details)


def add_borrow_record(user_id, book_id):
    borrow_ticket = Borrow(user_id=user_id)
    db.session.add(borrow_ticket)
    db.session.flush()

    detail = BorrowDetails(borrow_id=borrow_ticket.id, book_id=book_id)
    db.session.add(detail)

    book = Book.query.get(book_id)

    if book and book.quantity > 0:
        book.quantity -= 1
        if book.quantity == 0:
            book.available = False

        db.session.commit()
        return True

    db.session.rollback()
    return False


def cart_stats(cart):
    total_quantity = 0
    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
    return {'total_quantity': total_quantity}


def add_to_cart(cart, id, title):
    if not cart:
        cart = {}
    id = str(id)

    if id in cart:
        return cart, False
    else:
        cart[id] = {
            'id': id,
            'title': title,
            'quantity': 1
        }
    return cart, True


def add_multi_borrow_record(user_id, book_ids):
    try:
        borrow_ticket = Borrow(user_id=user_id)
        db.session.add(borrow_ticket)
        db.session.flush()

        for b_id in book_ids:
            book = Book.query.get(b_id)

            if book and book.quantity > 0:

                detail = BorrowDetails(book_id=book.id, borrow_id=borrow_ticket.id)
                db.session.add(detail)

                book.quantity -= 1
                if book.quantity == 0:
                    book.available = False
            else:
                db.session.rollback()
                return False, f"Sách '{book.title}' đã hết"

        db.session.commit()
        return True, "Mượn sách thành công!!!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def update_overdue_status():
    today = date.today()
    details = BorrowDetails.query.filter(
        BorrowDetails.status.in_([BorrowStatus.BORROWING, BorrowStatus.OVERDUE])
    ).all()

    late_days = 0
    for detail in details:
        due_date = detail.due_date.date() if isinstance(detail.due_date, datetime) else detail.due_date
        if due_date and today > due_date:
            detail.status = BorrowStatus.OVERDUE
            late_days = (today - due_date).days
            detail.fine = late_days * app.config['FINE_PER_DAY']

    db.session.commit()


def request_return_book(user_id, detail_id):
    detail = (db.session.query(BorrowDetails)
              .join(Borrow, Borrow.id == BorrowDetails.borrow_id)
              .join(Book, Book.id == BorrowDetails.book_id)
              .filter(BorrowDetails.id == detail_id)
              .first())
    if not detail:
        raise ValueError('Bản ghi mượn sách không tồn tại!')

    borrow = Borrow.query.get(detail.borrow_id)
    book = Book.query.get(detail.book_id)

    if not borrow:
        raise LookupError("Dữ liệu phiếu mượn không tồn tại!")

    if not book:
        raise LookupError('Dữ liệu sách không tồn tại!')

    if borrow.user_id != user_id:
        raise PermissionError("Bạn không có quyền gửi yêu cầu trả cuốn sách này!")

    if detail.status == BorrowStatus.RETURNED or detail.return_date is not None:
        raise ValueError("Cuốn sách này đã được trả rồi!")

    if detail.status == BorrowStatus.RETURNED_REQUEST:
        raise ValueError("Bạn đã gửi yêu cầu trả sách trước đó rồi!")

    detail.status = BorrowStatus.RETURNED_REQUEST
    db.session.commit()

    return detail


def approve_return_book(detail_id):
    detail = (db.session.query(BorrowDetails)
              .join(Borrow, Borrow.id == BorrowDetails.borrow_id)
              .join(Book, Book.id == BorrowDetails.book_id)
              .filter(BorrowDetails.id == detail_id)
              .first())

    if not detail:
        raise ValueError("Yêu cầu trả sách không tồn tại.")

    book = Book.query.get(detail.book_id)
    if not book:
        raise LookupError("Sách không tồn tại trong hệ thống.")

    if detail.status != BorrowStatus.RETURNED_REQUEST:
        raise ValueError("Cuốn sách này chưa ở trạng thái chờ duyệt trả.")


    detail.return_date = datetime.now()
    detail.status = BorrowStatus.RETURNED

    book.quantity = book.quantity + 1
    if book.quantity > 0:
        book.available = True

    db.session.commit()

    return {
        "detail_id": detail.id,
        "return_date": detail.return_date.strftime('%d/%m/%Y %H:%M:%S')
    }


def reject_return_request(detail_id):
    detail = BorrowDetails.query.filter_by(id=detail_id).first()

    if not detail:
        raise ValueError("Yêu cầu trả sách không tồn tại.")

    if detail.status != BorrowStatus.RETURNED_REQUEST:
        raise ValueError("Cuốn sách này không ở trạng thái chờ duyệt.")

    due_date = detail.due_date.date() if isinstance(detail.due_date, datetime) else detail.due_date
    today = date.today()

    if due_date and today > due_date:
        detail.status = BorrowStatus.OVERDUE
    else:
        detail.status = BorrowStatus.BORROWING

    db.session.commit()
    return detail


def get_return_requests():
    update_overdue_status()

    query = (db.session.query(BorrowDetails, Book, Borrow)
             .join(Borrow, Borrow.id == BorrowDetails.borrow_id)
             .join(Book, Book.id == BorrowDetails.book_id)
             .filter(BorrowDetails.status == BorrowStatus.RETURNED_REQUEST)
             .order_by(BorrowDetails.id.desc())
             .all())

    return query
def add_book(title, author, quantity, category_id, image=None):
    b = Book(
        title=title,
        author=author,
        quantity=quantity,
        category_id=category_id,
        image=image,
        available=True
    )
    db.session.add(b)
    db.session.commit()

def delete_book(book_id):
    b = Book.query.get(book_id)
    if not b:
        raise ValueError("Sách không tồn tại")
    is_used = BorrowDetails.query.filter_by(book_id=book_id).first()
    if is_used:
        raise Exception("Không thể xóa sách đang được mượn!")
    db.session.delete(b)
    db.session.commit()

def get_book_by_id(book_id):
    return Book.query.get(book_id)