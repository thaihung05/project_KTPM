from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, Float
from enum import Enum as UserEnum
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from eapp import db, app
import hashlib

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)

class UserRole(UserEnum):
    USER = 1
    ADMIN = 2

class BorrowStatus(UserEnum):
    BORROWING = 1
    RETURNED = 2

class User(BaseModel):
    name = Column(String(50), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    borrowed = relationship('Borrow', backref='user', lazy=True)

    def __repr__(self):
        return self.name

class Category(BaseModel):
    name = Column(String(50), nullable=False)

    books = relationship('Book', backref='category', lazy=True)

class Book(BaseModel):
    title = Column(String(50), nullable=False)
    author = Column(String(50))
    quantity = Column(Integer, default=0)
    available = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)

    borrowed_details = relationship('BorrowDetails', backref='book', lazy=True)

class Borrow(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    create_date = Column(DateTime, default=datetime.now)
    status = Column(Enum(BorrowStatus), default=BorrowStatus.BORROWING)

    details = relationship('BorrowDetails', backref='borrow', lazy=True)

def calculate_due_date():
    return datetime.now() + timedelta(app.config.get("due_time", 14))


class BorrowDetails(BaseModel):
    borrow_id = Column(Integer, ForeignKey('borrow.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    borrowed_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, default=calculate_due_date)
    return_date = Column(DateTime, nullable=True)
    fine = Column(Float, default=0)

    def is_overdue(self):
        if self.return_date:
            return self.return_date > self.due_date
        return datetime.now() > self.due_date


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        c1 = Category(name='Công nghệ thông tin')
        c2 = Category(name='Khoa học - Kỹ thuật')
        c3 = Category(name='Văn học - Nghệ thuật')
        c4 = Category(name='Kinh tế - Quản lý')
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()

        b1 = Book(title='Lập trình Python cơ bản', author='Thái Hùng', quantity=10, available=True, category_id=c1.id)
        b2 = Book(title='AI & Machine Learning', author='Lê Hùng', quantity=5, available=True, category_id=c1.id)
        b3 = Book(title='Lược sử loài người', author='Yuval Noah Harari', quantity=3, available=True, category_id=c2.id)
        b4 = Book(title='Nhà giả kim', author='Paulo Coelho', quantity=0, available=False, category_id=c3.id)
        b5 = Book(title='Cha giàu cha nghèo', author='Robert Kiyosaki', quantity=8, available=True, category_id=c4.id)
        db.session.add_all([b1, b2, b3, b4, b5])
        db.session.commit()

        u1 = User(name='Quản trị viên', username='admin',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.ADMIN)
        u2 = User(name='Thái Hùng', username='thaihung01',
                  password=hashlib.md5('Abc123'.encode()).hexdigest(), user_role=UserRole.USER)
        u3 = User(name='Nguyễn Văn Tèo', username='teonv',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u4 = User(name='Trần Thị Nụ', username='nutt',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER, active=False)
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        now = datetime.now()
        due_time = app.config.get("due_time", 14)

        borrow1 = Borrow(user_id=u2.id, create_date=now - timedelta(days=2), status=BorrowStatus.BORROWING)
        db.session.add(borrow1)
        db.session.commit()

        bd1 = BorrowDetails(borrow_id=borrow1.id, book_id=b1.id,
                            borrowed_date=now - timedelta(days=2),
                            due_date=now + timedelta(days=(due_time - 2)))
        db.session.add(bd1)

        borrow2 = Borrow(user_id=u3.id, create_date=now - timedelta(days=30), status=BorrowStatus.RETURNED)
        db.session.add(borrow2)
        db.session.commit()

        bd2 = BorrowDetails(borrow_id=borrow2.id,
                            book_id=b3.id,
                            borrowed_date=now - timedelta(days=30),
                            due_date=now - timedelta(days=16),
                            return_date=now - timedelta(days=20),
                            fine=0)
        db.session.add(bd2)

        borrow3 = Borrow(user_id=u3.id, create_date=now - timedelta(days=40), status=BorrowStatus.BORROWING)
        db.session.add(borrow3)
        db.session.commit()

        bd3 = BorrowDetails(borrow_id=borrow3.id, book_id=b5.id,
                            borrowed_date=now - timedelta(days=40),
                            due_date=now - timedelta(days=26))
        db.session.add(bd3)

        db.session.commit()