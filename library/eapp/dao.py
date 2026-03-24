from pymysql import IntegrityError

from eapp.models import Category, Book, UserRole, BorrowDetails, Borrow
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
