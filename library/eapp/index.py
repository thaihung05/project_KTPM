from asyncio import log

from flask import render_template, request, redirect, session
import math
from flask import jsonify
from eapp import app, dao, login
from flask_login import login_user, logout_user, current_user, login_required

from eapp.dao import register
from eapp.models import UserRole


def register_routes(app):
    @app.route('/login', methods=['GET'])
    def login_view():
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login_process():
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', err_msg='Vui lòng nhập đầy đủ thông tin!')

        user = dao.auth_user(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next') or request.form.get('next')
            if next_page:
                return redirect(next_page)
            if user.user_role == UserRole.ADMIN:
                return redirect('/admin/approve_request_view')
            else:
                return redirect('/books')
        return render_template('login.html', err_msg='Username hoặc password không chính xác!')

    @app.route('/register')
    def register_view():
        return render_template('register.html')

    @app.route('/register', methods=['POST'])
    def register_process():
        data = request.form

        username = data.get('username')
        password = data.get('password')
        confirm = data.get('confirm')
        name = data.get('name')

        if not username or not password or not confirm or not name:
            return render_template('register.html', err_msg='Vui lòng điền đầy đủ thông tin!')

        if password != confirm:
            return render_template('register.html', err_msg="Mật khẩu không khớp!")

        try:
            register(username=username, password=password, name=name)
            return redirect('/login')
        except Exception:
            return render_template('register.html', err_msg='Username này đã được đăng ký!!')
    @app.route('/logout')
    def logout_view():
        session.pop('cart', None)
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
        error_msg = None

        if kw and len(kw) == 1:
            error_msg = "Vui lòng nhập từ 2 ký tự trở lên để tìm kiếm sách!!!"
            books=[]
            total_pages =0
            categories = []
        else:
            categories = dao.load_categories()
            books = dao.load_books(kw=kw, search_by=search_by, cate_id=cate_id, page=pages)
            total_books = dao.count_books(kw=kw, cate_id=cate_id)
            total_pages = math.ceil(total_books / app.config['PAGE_SIZE'])

        return render_template('books.html', books=books, pages=total_pages, categories=categories, error_msg=error_msg)

    @app.route('/my_books_list')
    @login_required
    def my_book_list():
        error_msg = None
        try:
            all_borrowed_books = dao.load_all_borrowed_books(current_user.id)
            if not all_borrowed_books:
                error_msg = 'Chưa có sách!'
            return render_template('mybooks.html', all_borrowed_books=all_borrowed_books, error_msg=error_msg)
        except Exception as e:
            error_msg = f'Lỗi hệ thống: {str(e)}'
            return render_template('mybooks.html', all_borrowed_books=[], error_msg=error_msg), 500


    @app.route('/api/borrow/<int:book_id>', methods=['POST'])
    @login_required
    def api_borrow_books(book_id):
        if not current_user.active:
            return jsonify({'status': 403, 'message': 'Tài khoản của bạn đã bị khóa!!'}),403
        if dao.count_active_books(current_user.id) >= 5:
            return jsonify({'status': 400, 'message': 'Bạn chỉ có thể mượn tối đa 5 quyển sách!!'}),400
        if dao.has_overdue_books(current_user.id):
            return jsonify({'status': 400, 'message': 'Bạn có sách quá hạn chưa trả!!'}),400
        book = dao.get_book_by_id(book_id)
        if not book:
            return jsonify({
                'status': 404,
                'message': 'Sách không tồn tại trong hệ thống!!'
            }), 404
        if not isinstance(book.quantity, int) or book.quantity < 0:
            return jsonify({'status': 500, 'message': 'Dữ liệu sách lỗi'}), 500
        if book.quantity <= 0:
            return jsonify({'status': 400, 'message': f'Sách {book.title} không còn trong kho!!'}), 400
        try:
            if dao.add_borrow_record(current_user.id, book_id):
                return jsonify({
                    'status': 200,
                    'message': f'Mượn thành công {book.title}!!',
                    'new_quantity': book.quantity
                }), 200
            return jsonify({'status': 500, 'message': 'Hệ thống gặp lỗi!!'}), 500
        except Exception as e:
            return jsonify({'status': 500, 'message': 'Lỗi hệ thống (DB)'}), 500
    @app.route('/cart')
    @login_required
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

        return jsonify({'message': 'Sách này đã có trong danh sách!!'}), 400

    @app.route('/api/cart/<book_id>', methods=['DELETE'])
    @login_required
    def delete_cart(book_id):
        cart = session.get('cart', {})
        if cart and book_id in cart:
            del cart[book_id]
            session['cart'] = cart
            return jsonify(dao.cart_stats(cart))
        return jsonify({'message': 'Không tìm thấy sách!!'}), 404

    @app.route('/api/confirm-borrow', methods=['POST'])
    @login_required
    def confirm_borrow():
        data = request.json
        book_ids = data.get('book_ids', [])

        if not book_ids:
            return jsonify({'status': 400, 'message': 'Vui lòng chọn ít nhất một quyển sách để mượn!'}), 400
        if not current_user.active:
            return jsonify({'status': 403, 'message': 'Tài khoản của bạn đang bị khóa!'}), 403

        active_count = dao.count_active_books(current_user.id)
        if active_count + len(book_ids) > 5:
            return jsonify({'status': 400,
                            'message': f'Bạn đang mượn {active_count} quyển, chỉ được chọn thêm {5 - active_count} quyển nữa thôi!'}), 400

        if dao.has_overdue_books(current_user.id):
            return jsonify({'status': 400, 'message': 'Bạn còn sách quá hạn chưa trả, trả xong mới được mượn tiếp!'}), 400
        try:
            success, msg = dao.add_multi_borrow_record(current_user.id, book_ids)

            if success:
                cart = session.get('cart', {})
                for b_id in book_ids:
                    if str(b_id) in cart:
                        del cart[str(b_id)]
                session['cart'] = cart
                return jsonify({'status': 200, 'message': msg})
            return jsonify({'status': 500, 'message': msg})
        except Exception as e:
            return jsonify({'status': 500, 'message': f'Lỗi hệ thống: {str(e)}'}), 500
    @app.route('/api/return-request/<int:detail_id>', methods=['POST'])
    @login_required
    def api_request_return_book(detail_id):
        try:
            detail = dao.request_return_book(user_id=current_user.id, detail_id=detail_id)

            return jsonify({
                "detail_id": detail.id,
                "status": detail.status.value,
                "message": "Gửi yêu cầu trả sách thành công. Vui lòng chờ ADMIN duyệt."
            }), 200

        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except LookupError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500

    @app.route('/admin/approve_request_view')
    @login_required
    def admin_aprrove_request_view():
        requests = dao.get_return_requests()
        return render_template('admin_approve_request.html', requests=requests)

    @app.route('/api/admin/approve-return/<int:detail_id>', methods=['POST'])
    @login_required
    def api_approve_return(detail_id):
        if current_user.user_role != UserRole.ADMIN:
            return jsonify({"error": "Bạn không có quyền thực hiện chức năng này"}), 403

        try:
            result = dao.approve_return_book(detail_id)
            return jsonify({
                "message": "Duyệt trả sách thành công.",
                "data": result
            }), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except LookupError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500

    @app.route('/api/admin/reject-return/<int:detail_id>', methods=['POST'])
    @login_required
    def api_reject_return(detail_id):
        if current_user.user_role != UserRole.ADMIN:
            return jsonify({"error": "Bạn không có quyền thực hiện chức năng này"}), 403

        try:
            detail = dao.reject_return_request(detail_id)
            return jsonify({
                "message": "Đã từ chối yêu cầu trả sách.",
                "detail_id": detail.id,
                "status": detail.status.value
            }), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500


    @app.route('/my_borrowed_books')
    @login_required
    def my_borrowed_book():
        error_msg=None
        try:
            my_borrowed_books= dao.load_borrowed_books(current_user.id)
            if not my_borrowed_books:
                error_msg = 'Chưa có sách đã mượn!'
            return render_template('mybooks.html', my_borrowed_books=my_borrowed_books, error_msg=error_msg)
        except Exception as e:
            error_msg = f'Lỗi hệ thống: {str(e)}'
            return render_template('mybooks.html', my_borrowed_books=[], error_msg=error_msg), 500




    @app.route('/my_borrowing_books')
    @login_required
    def my_borrowing_book():
        error_msg=None
        try:
            my_borrowing_books= dao.load_borrowing_books(current_user.id)
            if not my_borrowing_books :
                error_msg='Chưa có sách đang mượn!'
            return render_template('mybooks.html',my_borrowing_books=my_borrowing_books,error_msg=error_msg)
        except Exception as e:
            error_msg = f'Lỗi hệ thống: {str(e)}'
            return render_template('mybooks.html', my_borrowing_books=[], error_msg=error_msg), 500

    @app.route('/admin/admin_books')
    @login_required
    def admin_books():
        if current_user.user_role != UserRole.ADMIN:
            return redirect('/')
        page = request.args.get('page', 1, type=int)
        total_books = dao.count_books()
        total_pages = math.ceil(total_books / app.config['PAGE_SIZE'])
        books = dao.load_books(page=page, page_size=app.config['PAGE_SIZE'])
        categories = dao.load_categories()
        return render_template('admin_books.html',pages=total_pages, books=books, categories=categories)

    @app.route('/api/admin/books', methods=['POST'])
    @login_required
    def add_book():
        title = request.form.get('title')
        author = request.form.get('author')
        quantity = request.form.get('quantity')
        category_id = request.form.get('category_id')

        image = request.files.get('image')

        image_url = None
        if image:
            import cloudinary.uploader
            res = cloudinary.uploader.upload(image)
            image_url = res.get('secure_url')

        dao.add_book(
            title=title,
            author=author,
            quantity=quantity,
            category_id=category_id,
            image=image_url
        )

        return jsonify({'message': 'Thêm sách thành công'})

    @app.route('/api/admin/books/<int:book_id>', methods=['DELETE'])
    @login_required
    def delete_book(book_id):
        if current_user.user_role != UserRole.ADMIN:
            return jsonify({'error': 'Không có quyền'}), 403

        try:
            dao.delete_book(book_id)
            return jsonify({'message': 'Xóa sách thành công'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.context_processor
def context_processor():
    return {'cart_stats': dao.cart_stats(session.get('cart'))}


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


if __name__ == '__main__':
    register_routes(app)
    app.run(debug=True)
