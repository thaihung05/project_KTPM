import hashlib

from flask import render_template, request, redirect, url_for
import math

from pymysql import IntegrityError

from eapp import app, dao, login, db
from flask_login import login_user, logout_user, current_user

from eapp.dao import register
from eapp.models import UserRole, User


@app.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username, password)
    if user:
        login_user(user)
        next_page = request.args.get('next') or request.form.get('next')
        if next_page:
            return redirect(next_page)
        if user.user_role == UserRole.ADMIN:
            return redirect('/admin')
        return redirect('/')
    return render_template('login.html', err_msg='Username hoặc password không chính xác!')

@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_process():
    data = request.form

    password = data.get('password')
    confirm = data.get('confirm')
    if password != confirm:
        err_msg = "Mật khẩu không khớp!"
        return render_template('register.html', err_msg=err_msg)

    try:
        register(username=data.get('username'),
                 password=password,
                 name=data.get('name'))
        return redirect('/login')

    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))

@app.route('/logout')
def logout_view():
    logout_user()
    return redirect('/')

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


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)
if __name__ == '__main__':
    app.run()