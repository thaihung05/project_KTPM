from eapp.models import Category, Book
from eapp import db, app

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
        query = query.filter(Book.title.contains(kw))

    if cate_id:
        if search_by == 'author':
            query = query.filter(Book.author.contains(kw))
        elif search_by == 'title':
            query = query.filter(Book.title.contains(kw))

    return query.count()