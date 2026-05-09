from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, Float
from enum import Enum as UserEnum
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from eapp import db, app
import hashlib
from flask_login import UserMixin


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
    OVERDUE = 3
    RETURNED_REQUEST = 4


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    borrowed = relationship('Borrow', backref='user', lazy=True)
    avatar = Column(String(255),
                    default='https://res.cloudinary.com/dx4i4a03w/image/upload/v1767614792/restaurant/avatars/uvp1wsa1gsqmcmpnfcev.jpg')

    def __repr__(self):
        return self.name


class Category(BaseModel):
    name = Column(String(50), nullable=False)

    books = relationship('Book', backref='category', lazy=True)


class Book(BaseModel):
    title = Column(String(500), nullable=False)
    author = Column(String(50))
    quantity = Column(Integer, default=0)
    available = Column(Boolean, default=True)
    image = Column(String(255), nullable=True)

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    borrowed_details = relationship('BorrowDetails', backref='book', lazy=True)


class Borrow(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    create_date = Column(DateTime, default=datetime.now)

    details = relationship('BorrowDetails', backref='borrow', lazy=True)


def calculate_due_date():
    return datetime.now() + timedelta(app.config.get("due_time", 14))


class BorrowDetails(BaseModel):
    borrow_id = Column(Integer, ForeignKey('borrow.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    borrowed_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, default=calculate_due_date)
    return_date = Column(DateTime, nullable=True)
    status = Column(Enum(BorrowStatus), default=BorrowStatus.BORROWING)
    fine = Column(Float, default=0)

    def is_overdue(self):
        if self.return_date:
            return self.return_date > self.due_date
        return datetime.now() > self.due_date


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        c1 = Category(name='Công nghệ thông tin')
        c2 = Category(name='Văn học Việt Nam')
        c3 = Category(name='Kinh tế - Quản lý')
        c4 = Category(name='Kỹ năng sống - Tâm lý')
        c5 = Category(name='Văn hóa - Thể thao - Ẩm thực')
        db.session.add_all([c1, c2, c3, c4, c5])
        db.session.commit()

        u1 = User(name='Quản trị viên', username='admin',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.ADMIN)
        u2 = User(name='Thái Hùng', username='thaihung01',
                  password=hashlib.md5('Abc123'.encode()).hexdigest(), user_role=UserRole.USER)
        u3 = User(name='Thanh Huy', username='huy01',
                  password=hashlib.md5('123'.encode()).hexdigest(), user_role=UserRole.USER)
        u4 = User(name='Văn Long', username='vanlong01',
                  password=hashlib.md5('Abc123'.encode()).hexdigest(), user_role=UserRole.USER)
        u5 = User(name='User 5 sách', username='test5books',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u6 = User(name='User 4 sách', username='test4books',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u7 = User(name='User 1 sách', username='test1books',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u8 = User(name='User locked', username='testlocked',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER, active=False)
        u9 = User(name='User 3 Sách', username='test3books',
                  password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u10 = User(name='User Quá Hạn', username='useroverdue',
                   password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u11 = User(name='User Đã Trả Quá Hạn', username='userreturnedoverdue',
                   password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)
        u12 = User(name='User Trả Đúng Hạn', username='userreturnedontime',
                   password=hashlib.md5('123456'.encode()).hexdigest(), user_role=UserRole.USER)

        db.session.add_all([u1, u2, u3, u4, u5, u6, u7, u8, u9, u10, u11, u12])
        db.session.commit()
        IMG_PATH = 'static/images/books/'

        books_data = [
            {'title': 'Cấu trúc dữ liệu và giải thuật', 'author': 'Lê Minh Hoàng', 'quantity': 0, 'cat': c1.id,
             'image': IMG_PATH + 'ctdl_gt_leminhhoang.jpg'},
            {'title': 'Giáo trình Ngôn ngữ lập trình C++', 'author': 'Vũ Việt Vũ', 'quantity': 25, 'cat': c1.id,
             'image': IMG_PATH + 'gt_vvv.jpg'},
            {'title': 'Nhập môn mạng máy tính', 'author': 'Hồ Đắc Phương', 'quantity': 20, 'cat': c1.id,
             'image': IMG_PATH + 'mang_may_tinh.jpg'},
            {'title': 'Lập trình ứng dụng di động với Flutter', 'author': 'Nguyễn Tiến Huy', 'quantity': 15,
             'cat': c1.id, 'image': IMG_PATH + 'flutter.jpg'},
            {'title': 'An toàn và bảo mật thông tin', 'author': 'Trần Đức Sự', 'quantity': 18, 'cat': c1.id,
             'image': IMG_PATH + 'atbm_thongtin.jpg'},
            {'title': 'Giáo trình Hệ điều hành', 'author': 'Trần Trung Dũng', 'quantity': 22, 'cat': c1.id,
             'image': IMG_PATH + 'he_dieu_hanh.jpg'},
            {'title': 'Giáo trình lập trình Python', 'author': 'Trần Đăng Hưng', 'quantity': 12, 'cat': c1.id,
             'image': IMG_PATH + 'laptrinh_python.jpg'},
            {'title': 'Quản trị Cơ sở dữ liệu MySQL', 'author': 'Trần Quang Thân', 'quantity': 10, 'cat': c1.id,
             'image': IMG_PATH + 'mysql.jpg'},
            {'title': 'Thiết kế Web cơ bản với HTML, CSS, JS', 'author': 'Huỳnh Xuân Hiệp', 'quantity': 35,
             'cat': c1.id, 'image': IMG_PATH + 'html_css_js.jpg'},
            {'title': 'Phân tích và thiết kế hệ thống thông tin', 'author': 'Nguyễn Văn Ba', 'quantity': 14,
             'cat': c1.id, 'image': IMG_PATH + 'pttk_httt.jpg'},
            {'title': 'Giáo trình Trí tuệ nhân tạo', 'author': 'Nguyễn Trường Thịnh', 'quantity': 8, 'cat': c1.id,
             'image': IMG_PATH + 'ai.jpg'},
            {'title': 'Lập trình Java core', 'author': 'Phạm Xuân Lân', 'quantity': 17, 'cat': c1.id,
             'image': IMG_PATH + 'java_core.jpg'},
            {'title': 'Hệ thống nhúng và IoT', 'author': 'Đỗ Văn Đỉnh', 'quantity': 11, 'cat': c1.id,
             'image': IMG_PATH + 'embedded_iot.jpg'},
            {'title': 'Quản lý dự án phần mềm theo Agile/Scrum', 'author': 'Andrew Pham và Phuong - Van Pham',
             'quantity': 1, 'cat': c1.id, 'image': IMG_PATH + 'agile_scrum.jpg'},
            {'title': 'Nhập môn Công nghệ phần mềm', 'author': 'Dương Hữu Thành', 'quantity': 1, 'cat': c1.id,
             'image': IMG_PATH + 'nhapmon_cnpm.jpg'},

            {'title': 'Truyện Kiều', 'author': 'Nguyễn Du', 'quantity': 50, 'cat': c2.id,
             'image': IMG_PATH + 'truyen_kieu.jpg'},
            {'title': 'Dế Mèn phiêu lưu ký', 'author': 'Tô Hoài', 'quantity': 45, 'cat': c2.id,
             'image': IMG_PATH + 'demen_plk.jpg'},
            {'title': 'Số đỏ', 'author': 'Vũ Trọng Phụng', 'quantity': 30, 'cat': c2.id,
             'image': IMG_PATH + 'so_do.jpg'},
            {'title': 'Chí Phèo', 'author': 'Nam Cao', 'quantity': 35, 'cat': c2.id,
             'image': IMG_PATH + 'chi_pheo.jpg'},
            {'title': 'Mắt biếc', 'author': 'Nguyễn Nhật Ánh', 'quantity': 40, 'cat': c2.id,
             'image': IMG_PATH + 'mat_biec.jpg'},
            {'title': 'Tôi thấy hoa vàng trên cỏ xanh', 'author': 'Nguyễn Nhật Ánh', 'quantity': 1, 'cat': c2.id,
             'image': IMG_PATH + 'toi_thay_hoa_vang.jpg'},
            {'title': 'Cánh đồng bất tận', 'author': 'Nguyễn Ngọc Tư', 'quantity': 20, 'cat': c2.id,
             'image': IMG_PATH + 'canh_dong_bat_tan.jpg'},
            {'title': 'Vang bóng một thời', 'author': 'Nguyễn Tuân', 'quantity': 15, 'cat': c2.id,
             'image': IMG_PATH + 'vang_bong.jpg'},
            {'title': 'Tắt đèn', 'author': 'Ngô Tất Tố', 'quantity': 28, 'cat': c2.id,
             'image': IMG_PATH + 'tat_den.jpg'},
            {'title': 'Đất rừng phương Nam', 'author': 'Đoàn Giỏi', 'quantity': 32, 'cat': c2.id,
             'image': IMG_PATH + 'dat_rung_phuong_nam.jpg'},
            {'title': 'Bến không chồng', 'author': 'Dương Hướng', 'quantity': 18, 'cat': c2.id,
             'image': IMG_PATH + 'ben_khong_chong.jpg'},
            {'title': 'Nỗi buồn chiến tranh', 'author': 'Bảo Ninh', 'quantity': 22, 'cat': c2.id,
             'image': IMG_PATH + 'noi_buon_chien_tranh.jpg'},
            {'title': 'Thời xa vắng', 'author': 'Lê Lựu', 'quantity': 14, 'cat': c2.id,
             'image': IMG_PATH + 'thoi_xa_vang.jpg'},
            {'title': 'Mùa lá rụng trong vườn', 'author': 'Ma Văn Kháng', 'quantity': 16, 'cat': c2.id,
             'image': IMG_PATH + 'mua_la_rung.jpg'},
            {'title': 'Sông xa', 'author': 'Chu Lai', 'quantity': 12, 'cat': c2.id, 'image': IMG_PATH + 'song_xa.jpg'},

            {'title': 'Trên đường băng', 'author': 'Tony Buổi Sáng', 'quantity': 40, 'cat': c3.id,
             'image': IMG_PATH + 'tren_duong_bang.jpg'},
            {'title': 'Cà phê cùng Tony', 'author': 'Tony Buổi Sáng', 'quantity': 38, 'cat': c3.id,
             'image': IMG_PATH + 'caphe_cung_tony.jpg'},
            {'title': 'Nhà lãnh đạo không chức danh', 'author': 'Robin Sharma', 'quantity': 35, 'cat': c3.id,
             'image': IMG_PATH + 'nld_khong_chuc_danh.jpg'},
            {'title': 'Nghĩ giàu làm giàu', 'author': 'Napoleon Hill', 'quantity': 30, 'cat': c3.id,
             'image': IMG_PATH + 'nghi_giau_lam_giau.jpg'},
            {'title': 'Marketing căn bản', 'author': 'Hoàng Thị Phương Thảo', 'quantity': 25, 'cat': c3.id,
             'image': IMG_PATH + 'marketing_can_ban.jpg'},
            {'title': 'Giáo trình quản trị kinh doanh', 'author': 'Nguyễn Ngọc Huyền', 'quantity': 20, 'cat': c3.id,
             'image': IMG_PATH + 'qtkd.jpg'},
            {'title': 'Kế toán tài chính DN', 'author': 'Trương Thị Thủy & Ngô Thị Thu Hồng', 'quantity': 28,
             'cat': c3.id, 'image': IMG_PATH + 'ketoan_dn.jpg'},
            {'title': 'Đầu tư chứng khoán theo chỉ số', 'author': 'John C. Bogle', 'quantity': 15, 'cat': c3.id,
             'image': IMG_PATH + 'stock_investment.jpg'},
            {'title': 'Phân tích dữ liệu kinh doanh', 'author': 'Nguyễn Đình Thuân', 'quantity': 18, 'cat': c3.id,
             'image': IMG_PATH + 'business_data_anal.jpg'},
            {'title': 'Kỹ năng bán hàng đỉnh cao', 'author': 'Vương Nghị', 'quantity': 22, 'cat': c3.id,
             'image': IMG_PATH + 'skill_selling.jpg'},
            {'title': 'QUẢN TRỊ NHÂN SỰ ĐÚNG NGAY TỪ ĐẦU', 'author': 'Hồng Duyên', 'quantity': 17, 'cat': c3.id,
             'image': IMG_PATH + 'hr_practice.jpg'},
            {'title': 'Logistics và quản lý chuỗi cung ứng', 'author': 'Paul R. Murphy, Jr., A. Michael Knemeyer',
             'quantity': 14, 'cat': c3.id, 'image': IMG_PATH + 'logistics.jpg'},
            {'title': 'Hành vi tổ chức', 'author': 'Nguyễn Quang Vinh', 'quantity': 12, 'cat': c3.id,
             'image': IMG_PATH + 'org_behavior.jpg'},
            {'title': 'Giao trình thương mại điện tử', 'author': 'Phạm Thị Thanh Hồng', 'quantity': 16, 'cat': c3.id,
             'image': IMG_PATH + 'ecommerce.jpg'},
            {'title': 'Giá Trong Chiến Lược Kinh Doanh', 'author': 'Hidenobu Senga', 'quantity': 11, 'cat': c3.id,
             'image': IMG_PATH + 'price_strategy.jpg'},

            {'title': 'Tuổi trẻ đáng giá bao nhiêu?', 'author': 'Rosie Nguyễn', 'quantity': 50, 'cat': c4.id,
             'image': IMG_PATH + 'tuoi_tre_dang_gia.jpg'},
            {'title': 'Đắc Nhân Tâm', 'author': 'Dale Carnegie (Dịch giả VN)', 'quantity': 50, 'cat': c4.id,
             'image': IMG_PATH + 'dac_nhan_tam.jpg'},
            {'title': 'Hành trình về Phương Đông', 'author': 'Baird T. Spalding (Nguyên Phong dịch)', 'quantity': 45,
             'cat': c4.id, 'image': IMG_PATH + 'hanhtrinh_phuongdong.jpg'},
            {'title': 'Dấu chân trên cát', 'author': 'Nguyên Phong', 'quantity': 35, 'cat': c4.id,
             'image': IMG_PATH + 'dau_chan_tren_cat.jpg'},
            {'title': 'Khéo ăn nói sẽ có được thiên hạ', 'author': 'Trác Nhã (Dịch giả VN)', 'quantity': 40,
             'cat': c4.id, 'image': IMG_PATH + 'kheo_an_noi.jpg'},
            {'title': 'Rèn luyện tư duy phản biện', 'author': 'Albert Rutherford', 'quantity': 20, 'cat': c4.id,
             'image': IMG_PATH + 'critical_thinking.jpg'},
            {'title': 'Tâm lý học đám đông', 'author': 'Gustave Le Bon (Dịch giả VN)', 'quantity': 18, 'cat': c4.id,
             'image': IMG_PATH + 'psyc_crowd.jpg'},
            {'title': 'Hiểu về trái tim', 'author': 'Minh Niệm', 'quantity': 38, 'cat': c4.id,
             'image': IMG_PATH + 'hieu_ve_trai_tim.jpg'},
            {'title': 'Lối sống tối giản của người Nhật', 'author': 'Sasaki Fumio (Dịch giả VN)', 'quantity': 30,
             'cat': c4.id, 'image': IMG_PATH + 'minimalism.jpg'},
            {'title': 'Nghệ thuật quản lý thời gian', 'author': 'Brian Tracy', 'quantity': 22, 'cat': c4.id,
             'image': IMG_PATH + 'time_management.jpg'},
            {'title': 'Làm chủ cảm xúc', 'author': 'Nguyễn Tâm Lý', 'quantity': 17, 'cat': c4.id,
             'image': IMG_PATH + 'master_emotion.jpg'},
            {'title': 'Nghệ thuật nói trước công chúng', 'author': 'Dale Carnegie', 'quantity': 15, 'cat': c4.id,
             'image': IMG_PATH + 'presentation_skill.jpg'},
            {'title': 'Dọn dẹp nhà cửa dọn dẹp tâm trí', 'author': 'Marie Kondo (Dịch giả VN)', 'quantity': 25,
             'cat': c4.id, 'image': IMG_PATH + 'spark_joy.jpg'},
            {'title': 'Bí mật của may mắn', 'author': 'Alex Rovira (Dịch giả VN)', 'quantity': 28, 'cat': c4.id,
             'image': IMG_PATH + 'good_luck.jpg'},
            {'title': 'Thay thái độ đổi cuộc đời', 'author': 'Keith D. Harrell (Dịch giả VN)', 'quantity': 14,
             'cat': c4.id, 'image': IMG_PATH + 'change_attitude.jpg'},

            {'title': 'Nét đẹp văn hóa miệt vườn', 'author': 'Sơn Nam', 'quantity': 25, 'cat': c5.id,
             'image': IMG_PATH + 'vanhoa_mietvuon.jpg'},
            {'title': 'Sài Gòn năm xưa', 'author': 'Vương Hồng Sển', 'quantity': 22, 'cat': c5.id,
             'image': IMG_PATH + 'saigon_nam_xuya.jpg'},
            {'title': 'Vovinam Việt Võ Đạo cơ bản', 'author': 'Sáng tổ Nguyễn Lộc', 'quantity': 30, 'cat': c5.id,
             'image': IMG_PATH + 'vovinam_basic.jpg'},
            {'title': 'Kỹ thuật Võ cổ truyền Việt Nam', 'author': 'Lê Kim Hòa', 'quantity': 20, 'cat': c5.id,
             'image': IMG_PATH + 'vocotruyen_vn.jpg'},
            {'title': 'Khám phá ẩm thực truyền thống Việt Nam', 'author': 'Ngô Đức Thịnh', 'quantity': 35, 'cat': c5.id,
             'image': IMG_PATH + 'cuisine_vn.jpg'},
            {'title': 'Vovinam phân thế Nhu khí công quyền', 'author': 'Chưởng môn Lê Sáng', 'quantity': 15,
             'cat': c5.id, 'image': IMG_PATH + 'vovinam_advanced.jpg'},
            {'title': 'Di Tích Lịch Sử Văn Hóa TPHCM', 'author': 'Nhiều tác giả', 'quantity': 18, 'cat': c5.id,
             'image': IMG_PATH + 'ditich_saigon.jpg'},
            {'title': 'Nghệ thuật đờn ca tài tử Nam Bộ', 'author': 'Nguyễn Phúc An', 'quantity': 12, 'cat': c5.id,
             'image': IMG_PATH + 'don_ca_tai_tu.jpg'},
            {'title': 'Lịch sử Việt Nam bằng tranh', 'author': 'Trần Bạch Đằng (Chủ biên)', 'quantity': 40,
             'cat': c5.id, 'image': IMG_PATH + 'history_comics.jpg'},
            {'title': 'Hướng dẫn khởi động & 200 tư thế yoga từ cơ bản tới nâng cao', 'author': 'Phan Thị Nga',
             'quantity': 28, 'cat': c5.id, 'image': IMG_PATH + 'yoga_home.jpg'},
            {'title': 'Kinh doanh ẩm thực đường phố', 'author': 'Đoàn Văn Minh Nhật', 'quantity': 30, 'cat': c5.id,
             'image': IMG_PATH + 'street_food.jpg'},
            {'title': 'Văn hóa Trà Việt', 'author': 'Hà Huy Thanh', 'quantity': 14, 'cat': c5.id,
             'image': IMG_PATH + 'tea_culture.jpg'},
            {'title': 'HỆ THỐNG BÀI TẬP NÂNG CAO KỸ- CHIẾN THUẬT BÓNG ĐÁ',
             'author': 'PGS.TS. Trần Duy Hòa – TS. Võ Văn Quyết', 'quantity': 17, 'cat': c5.id,
             'image': IMG_PATH + 'football_basic.jpg'},
            {'title': 'Thư pháp Việt', 'author': 'Đăng Học', 'quantity': 11, 'cat': c5.id,
             'image': IMG_PATH + 'calligraphy_vn.jpg'},
            {'title': 'Phở và các món nước', 'author': 'Bùi Thị Sương', 'quantity': 25, 'cat': c5.id,
             'image': IMG_PATH + 'cooking_pho.jpg'}
        ]

        for item in books_data:
            b = Book(
                title=item['title'],
                author=item['author'],
                quantity=item['quantity'],
                available=(item['quantity'] > 0),
                category_id=item['cat'],
                image=item['image']
            )
            db.session.add(b)

        db.session.commit()

        for i in range(1, 61):
            b = Book(title=f"Sách lập trình Python tập {i}",
                     category_id=1)
            db.session.add(b)
        db.session.commit()
        print("Đã bơm xong 60 cuốn sách!")

        future = datetime.now() + timedelta(days=10)
        past = datetime.now() - timedelta(days=5)

        # user5books: 5 cuốn đang mượn (book id 1–5)
        for book_id in range(1, 6):
            br = Borrow(user_id=u5.id)
            db.session.add(br)
            db.session.flush()
            db.session.add(BorrowDetails(borrow_id=br.id, book_id=book_id, due_date=future))
        db.session.commit()

        # user4books: 4 cuốn đang mượn (book id 1–4)
        for book_id in range(1, 5):
            br = Borrow(user_id=u6.id)
            db.session.add(br)
            db.session.flush()
            db.session.add(BorrowDetails(borrow_id=br.id, book_id=book_id, due_date=future))
        db.session.commit()

        # user1book: 1 cuốn đang mượn (book id 1)
        br = Borrow(user_id=u7.id)
        db.session.add(br)
        db.session.flush()
        db.session.add(BorrowDetails(borrow_id=br.id, book_id=1, due_date=future))
        db.session.commit()

        # user3books: 3 cuốn đang mượn (book id 1–3)
        for book_id in range(1, 4):
            br = Borrow(user_id=u9.id)
            db.session.add(br)
            db.session.flush()
            db.session.add(BorrowDetails(borrow_id=br.id, book_id=book_id, due_date=future))
        db.session.commit()

        # useroverdue: 1 cuốn quá hạn (book id 1, due_date đã qua)
        br = Borrow(user_id=u10.id)
        db.session.add(br)
        db.session.flush()
        db.session.add(BorrowDetails(
            borrow_id=br.id, book_id=1,
            due_date=past,
            status=BorrowStatus.OVERDUE
        ))
        db.session.commit()

        # userreturnedoverdue: đã từng có sách quá hạn nhưng đã trả rồi
        # due_date = 20 ngày trước, return_date = 10 ngày trước → trả muộn 10 ngày
        very_past_due = datetime.now() - timedelta(days=20)
        very_past_return = datetime.now() - timedelta(days=10)
        br = Borrow(user_id=u11.id)
        db.session.add(br)
        db.session.flush()
        db.session.add(BorrowDetails(
            borrow_id=br.id, book_id=2,
            due_date=very_past_due,
            return_date=very_past_return,
            status=BorrowStatus.RETURNED
        ))
        db.session.commit()

        # userreturnedontime: đã từng mượn và trả đúng hạn (trước due_date)
        # due_date = 10 ngày trước, return_date = 15 ngày trước → trả trước hạn 5 ngày
        on_time_due = datetime.now() - timedelta(days=10)
        on_time_return = datetime.now() - timedelta(days=15)
        br = Borrow(user_id=u12.id)
        db.session.add(br)
        db.session.flush()
        db.session.add(BorrowDetails(
            borrow_id=br.id, book_id=3,
            due_date=on_time_due,
            return_date=on_time_return,
            status=BorrowStatus.RETURNED
        ))
        db.session.commit()

        print("Đã tạo xong test users cho Selenium!")

