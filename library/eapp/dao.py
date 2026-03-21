from eapp.models import Category, Book
from eapp import db, app

def load_categories():
    categories = Category.query.all()

def load_book(kw=None, cate_id=None, page=1):
    query = Book.query

    if kw:
        query = query.filter(Book.name.contains(kw))

    if cate_id:
        query = query.filter(Book.category_id.__eq__(cate_id))

    if page:
        start = (page - 1) * app.config['PAGE_SIZE']
        query = query.slice(start, start + app.config['PAGE_SIZE'])

    return query.all()
