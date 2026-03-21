from flask import render_template, request
import math
from eapp import app, dao



@app.route('/')
def index():
    books = dao.load_books(page=1, page_size=10)

    return render_template('index.html', books=books)

@app.route('/books')
def book_list():
    kw = request.args.get('kw')
    cate_id = request.args.get('category_id')
    page = request.args.get('page', 1, type=int)
    search_by = request.args.get('search_by', 'title')

    categories = dao.load_categories()
    books = dao.load_books(kw=kw, search_by= search_by, cate_id=cate_id, page=page)

    total_books = dao.count_books(kw=kw, cate_id=cate_id)
    pages = math.ceil(total_books / app.config['PAGE_SIZE'])

    return render_template('books.html', books=books, pages=pages, categories=categories)

if __name__ == '__main__':
    app.run()