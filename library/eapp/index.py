from flask import render_template, request, redirect, session
import math
from flask import jsonify
from eapp import app, dao, login, db
from flask_login import login_user, logout_user, current_user, login_required

from eapp.dao import register
from eapp.models import UserRole


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
        return render_template('register.html', err_msg='Username này đã được đăng ký!!')


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
    pages = request.args.get('page', 1, type=int)
    search_by = request.args.get('search_by', 'title')

    categories = dao.load_categories()
    books = dao.load_books(kw=kw, search_by=search_by, cate_id=cate_id, page=pages)

    error_msg = None
    books = []
    pages = 0
    categories = []
    if kw and len(kw) == 1:
        error_msg = "Vui lòng nhập từ 2 ký tự trở lên để tìm kiếm sách!!!"
    else:
        categories = dao.load_categories()
        books = dao.load_books(kw=kw, search_by= search_by, cate_id=cate_id, page=pages)
        total_books = dao.count_books(kw=kw, cate_id=cate_id)
        pages = math.ceil(total_books / app.config['PAGE_SIZE'])

    return render_template('books.html', books=books, pages=pages, categories=categories, error_msg=error_msg)




@app.route('/my_books_list')
def my_book_list():
    all_borrowed_books= dao.load_all_borrowed_books(current_user.id)
    error_msg=None

    if all_borrowed_books is None:
        error_msg='Chưa có sách mượn!'
    return render_template('mybooks.html', all_borrowed_books=all_borrowed_books, error_msg=error_msg)

@app.route('/my_borrowed_books')
def my_borrowed_book():
    my_borrowed_books= dao.load_borrowed_books(current_user.id)
    error_msg=None

    if my_borrowed_book is None:
        error_msg='Chưa có sách mượn'
    return render_template('mybooks.html',my_borrowed_books=my_borrowed_books,error_msg=error_msg)


@app.route('/my_borrowing_books')
def my_borrowing_book():
    my_borrowing_books= dao.load_borrowing_books(current_user.id)
    error_msg=None

    if my_borrowed_book is None:
        error_msg='Chưa có sách mượn'
    return render_template('mybooks.html',my_borrowing_books=my_borrowing_books,error_msg=error_msg)


# @app.route('/borrow/<int:book_id>', methods=['POST'])
# @login_required
# def borrow_process(book_id):
#     if not current_user.active:
#         flash("Tài khoản của bạn đã bị khóa!!Hãy liên lạc với admin để hiểu rõ hơn!!", "danger")
#         return redirect(url_for('book_list'))
#     if dao.count_active_books(current_user.id) > 5:
#         flash("Bạn chỉ có thể mượn tối đa 5 quyển sách!!", "Warning")
#         return redirect(url_for('book_list'))
#     if dao.has_overdue_books(current_user.id):
#         flash("Bạn đang nợ sách quá hạn!!", "danger")
#         return redirect(url_for('book_list'))
#     book = dao.Book.query.get(book_id)
#     if not book or book.quantity <=0:
#         flash("Sách đã hết bản!", "info")
#         return redirect(url_for('book_list'))
#     if dao.add_borrow_record(current_user.id, book_id):
#         flash(f"Mượn thành công {book.title}!!", "success")
#     return redirect(url_for('book_list'))

@app.route('/api/borrow/<int:book_id>', methods=['POST'])
@login_required
def api_borrow_books(book_id):
    if not current_user.active:
        return jsonify({'status': 403, 'message': 'Tài khoản của bạn đã bị khóa!!'})
    if dao.count_active_books(current_user.id) >= 5:
        return jsonify({'status': 400, 'message': 'Bạn chỉ có thể mượn tối đa 5 quyển sách!!'})
    if dao.has_overdue_books(current_user.id):
        return jsonify({'status': 400, 'message': 'Bạn có sách quá hạn chưa trả!!'})
    book = dao.Book.query.get(book_id)
    if not book or book.quantity <= 0:
        return jsonify({'status': 404, 'message': f'Sách {book.title} không còn trong kho!!'})

    if dao.add_borrow_record(current_user.id, book_id):
        return jsonify({
            'status': 200,
            'message': f'Mượn thành công {book.title}!!',
            'new_quantity': book.quantity
        })
    return jsonify({'status': 500, 'message': 'Hệ thống gặp lỗi!!'})

@app.context_processor
def context_processor():
    return {'cart_stats': dao.cart_stats(session.get('cart'))}

@app.route('/cart')
def cart_view():
    return render_template('cart.html', cart=session.get('cart', {}))

@app.route('/api/cart', methods=['POST'])
@login_required
def add_to_cart_api():
    data = request.json
    cart = session.get('cart', {})
    new_cart, is_added = dao.add_to_cart(cart, data.get('id'), data.get('title'))

    if is_added:
        session['cart'] = new_cart
        return jsonify(dao.cart_stats(new_cart))

    return jsonify({'message':'Sách này đã có trong danh sách!!'}), 400

@app.route('/api/cart/<book_id>', methods=['DELETE'])
def delete_cart(book_id):
    cart = session.get('cart', {})
    if cart and book_id in cart:
        del cart[book_id]
        session['cart'] = cart
        return jsonify(dao.cart_stats(cart))
    return jsonify({'message':'Không tìm thấy sách!!'}), 400



@app.route('/api/confirm-borrow', methods=['POST'])
@login_required
def confirm_borrow():
    data = request.json
    book_ids = data.get('book_ids', [])

    if not current_user.active:
        return jsonify({'status': 403, 'message': 'Tài khoản của bạn đang bị khóa!'})

    active_count = dao.count_active_books(current_user.id)
    if active_count + len(book_ids) > 5:
        return jsonify({'status': 400,
                        'message': f'Bạn đang mượn {active_count} quyển, chỉ được chọn thêm {5 - active_count} quyển nữa thôi!'})

    if dao.has_overdue_books(current_user.id):
        return jsonify({'status': 400, 'message': 'Bạn còn sách quá hạn chưa trả, trả xong mới được mượn tiếp!'})

    success, msg = dao.add_multi_borrow_record(current_user.id, book_ids)

    if success:
        cart = session.get('cart', {})
        for b_id in book_ids:
            if str(b_id) in cart:
                del cart[str(b_id)]
        session['cart'] = cart
        return jsonify({'status': 200, 'message': msg})

    return jsonify({'status': 500, 'message': msg})


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


if __name__ == '__main__':

    app.run(debug=True)

