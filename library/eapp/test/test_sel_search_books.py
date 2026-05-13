from selenium.webdriver.common.by import By

from eapp.test.test_base import driver
from eapp.test.search_helper import perform_search, assert_positive, assert_negative, assert_category_active,assert_pagination_active,perform_search_by_url


def test_search_full_title(driver):
    kw = "Truyện Kiều"
    results = perform_search(driver, kw, search_by="title")
    assert_positive(results, kw)

def test_search_full_title_but_none_book(driver):
    kw = "Sách tập thể hình 2026"
    results = perform_search(driver, kw, search_by="title")
    assert_negative(driver, results, kw)

def test_search_a_part_of_title(driver):
    kw = 'truyen'
    results = perform_search(driver, kw, search_by="title")
    assert_positive(results, kw)

def test_search_a_part_of_title_but_none_book(driver):
    kw = 'thể hình'
    results = perform_search(driver, kw, search_by="title")
    assert_negative(driver,results, kw)

def test_search_full_name_author(driver):
    kw = 'Trần Đăng Hưng'
    search_by='author'
    results = perform_search(driver, kw, search_by=search_by)
    assert_positive(results, kw, search_by=search_by)

def test_search_full_name_author_but_none_book(driver):
    kw = "Nguyễn Trãi"
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by)
    assert_negative(driver, results, kw)

def test_search_a_part_of_name_author(driver):
    kw = 'Trần'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by)
    assert_positive(results, kw, search_by=search_by)

def test_search_a_part_of_name_author_but_none_book(driver):
    kw = 'Trãi'
    search_by = "author"
    results = perform_search(driver, kw, search_by=search_by)
    assert_negative(driver,results, kw)

def test_filter_by_all_books(driver):
    c_name = 'Tất cả sách'

    driver.get("http://127.0.0.1:5000/books?category_id=3")

    results = perform_search(driver, c_name=c_name, open_page=False)

    assert_positive(results, kw=None)
    assert_category_active(driver, c_name)

def test_filter_by_category_it(driver):
    c_name = 'Công nghệ thông tin'

    results = perform_search(driver, c_name=c_name)

    assert_positive(results, kw=None)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_it(driver):
    c_name = 'Công nghệ thông tin'
    kw = 'python'
    search_by = 'title'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_it_but_none_book(driver):
    c_name = 'Công nghệ thông tin'
    kw = 'pythong'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_it(driver):
    c_name = 'Công nghệ thông tin'
    kw = 'Hồ Đắc Phương'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw, search_by=search_by)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_it_but_none_book(driver):
    c_name = 'Công nghệ thông tin'
    kw = 'Hồ Đắc Phùng'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_filter_by_category_vhvn(driver):
    c_name = 'Văn học Việt Nam'

    results = perform_search(driver, c_name=c_name)

    assert_positive(results, kw=None)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_vhvn(driver):
    c_name = 'Văn học Việt Nam'
    kw = 'Truyện Kiều'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_vhvn_but_none_book(driver):
    c_name = 'Văn học Việt Nam'
    kw = 'Truyện Này Nọ'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_vhvn(driver):
    c_name = 'Văn học Việt Nam'
    kw = 'Nguyễn Du'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw, search_by=search_by)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_vhvn_but_none_book(driver):
    c_name = 'Văn học Việt Nam'
    kw = 'Nguyễn Trãi'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_filter_by_category_ktql(driver):
    c_name = 'Kinh tế - Quản lý'

    results = perform_search(driver, c_name=c_name)

    assert_positive(results, kw=None)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_ktql(driver):
    c_name = 'Kinh tế - Quản lý'
    kw = 'Cà phê cùng Tony'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_ktql_but_none_book(driver):
    c_name = 'Kinh tế - Quản lý'
    kw = 'Cà phê cùng Tony Ken nè'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_ktql(driver):
    c_name = 'Kinh tế - Quản lý'
    kw = 'Tony'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw, search_by=search_by)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_ktql_but_none_book(driver):
    c_name = 'Kinh tế - Quản lý'
    kw = 'Tony Ken Bla Bla'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_filter_by_category_knstl(driver):
    c_name = 'Kỹ năng sống - Tâm lý'

    results = perform_search(driver, c_name=c_name)

    assert_positive(results, kw=None)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_knstl(driver):
    c_name = 'Kỹ năng sống - Tâm lý'
    kw = 'Đắc Nhân Tâm'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_knstl_but_none_book(driver):
    c_name = 'Kỹ năng sống - Tâm lý'
    kw = 'Đắc Nhân Tâm Lý Tội Phạm'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_knstl(driver):
    c_name = 'Kỹ năng sống - Tâm lý'
    kw = 'Dale Carnegie'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw, search_by=search_by)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_knstl_but_none_book(driver):
    c_name = 'Kỹ năng sống - Tâm lý'
    kw = 'Dale Carnegie Bergie Arcane'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_filter_by_category_vhttat(driver):
    c_name = 'Văn hóa - Thể thao - Ẩm thực'

    results = perform_search(driver, c_name=c_name)

    assert_positive(results, kw=None)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_vhttat(driver):
    c_name = 'Văn hóa - Thể thao - Ẩm thực'
    kw = 'Sài Gòn năm xưa'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_title_and_filter_by_category_vhttat_but_none_book(driver):
    c_name = 'Văn hóa - Thể thao - Ẩm thực'
    kw = 'Sài Gòn năm xưa lắc xưa lơ'
    search_by = 'title'

    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_vhttat(driver):
    c_name = 'Văn hóa - Thể thao - Ẩm thực'
    kw = 'Vương Hồng Sển'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_positive(results, kw, search_by=search_by)
    assert_category_active(driver, c_name)

def test_search_with_word_search_by_author_and_filter_by_category_vhttat_but_none_book(driver):
    c_name = 'Văn hóa - Thể thao - Ẩm thực'
    kw = 'Vương Hồng Sển Bengal Baka Naga'
    search_by = 'author'
    results = perform_search(driver, kw, search_by=search_by, c_name=c_name)

    assert_negative(driver, results, kw)
    assert_category_active(driver, c_name)

def test_lower_than_2_character(driver):
    kw = 'a'
    results = perform_search(driver, kw)
    assert_negative(driver, results, kw)

def test_kw_empty(driver):
    kw = ''
    driver.get("http://127.0.0.1:5000/books?category_id=3")
    results = perform_search(driver, kw, open_page=False)
    assert_positive(results, kw)

def test_kw_only_space(driver):
    kw = '           '
    driver.get("http://127.0.0.1:5000/books?category_id=3")
    results = perform_search(driver, kw, open_page=False)

    assert_positive(results, kw)

def test_kw_have_space(driver):
    kw = '              Lập trình Java Core                   '

    results = perform_search(driver, kw)
    assert_positive(results, kw)

def test_pagination_when_over_50_books(driver):

    results_1 = perform_search(driver)

    assert len(results_1) <= 50, f"Lỗi: Page 1 có hơn 50 sách ({len(results_1)})"

    first_book_1 = results_1[0].text

    results_2 = perform_search(driver,page=2,open_page=False)

    assert_pagination_active(driver, 2)

    assert len(results_2) > 0, "Lỗi: Page 2 không có dữ liệu"

    first_book_2 = results_2[0].text

    assert first_book_1 != first_book_2, "Lỗi: Dữ liệu page 1 và page 2 giống nhau"

def test_pagination_when_search_result_over_50_books(driver):

    kw = 'python'
    results_1 = perform_search(driver, kw)

    assert len(results_1) <= 50, f"Lỗi: Page 1 có hơn 50 sách ({len(results_1)})"

    first_book_1 = results_1[0].text

    results_2 = perform_search(driver,page=2,open_page=False)

    assert_pagination_active(driver, 2)

    assert len(results_2) > 0, "Lỗi: Page 2 không có dữ liệu"

    first_book_2 = results_2[0].text

    assert first_book_1 != first_book_2, "Lỗi: Dữ liệu page 1 và page 2 giống nhau"

def test_search_kw_on_url(driver):
    kw = 'Tôi thấy hoa vàng trên cỏ xanh'

    results = perform_search_by_url(driver,kw=kw)

    assert_positive(results, kw)

def test_search_author_on_url(driver):
    kw = 'Nguyễn Du'
    search_by = 'author'

    results = perform_search_by_url(driver,kw=kw,search_by=search_by)

    assert_positive(results, kw, search_by=search_by)

def test_search_title_on_url(driver):
    kw = 'Lập Trình Java Core'
    search_by = 'title'

    results = perform_search_by_url(driver,kw=kw,search_by=search_by)

    assert_positive(results, kw)

def test_search_author_kw_but_search_title_on_url(driver):
    kw = 'Nguyễn Du'
    search_by = 'title'

    results = perform_search_by_url(driver,kw=kw,search_by=search_by)

    assert_negative(driver, results, kw)

def test_search_title_kw_but_search_author_on_url(driver):
    kw = 'Lập Trình Java Core'
    search_by = 'author'

    results = perform_search_by_url(driver,kw=kw,search_by=search_by)

    assert_negative(driver, results, kw)

def test_search_kw_and_category_on_url(driver):
    kw = 'Tôi thấy hoa vàng trên cỏ xanh'

    results = perform_search_by_url(driver,kw=kw,c_name=2)

    assert_positive(results, kw)

def test_search_kw_lower_than_2_character_on_url(driver):
    kw = 'a'

    results = perform_search_by_url(driver,kw=kw)

    assert_negative(driver, results, kw)

def test_search_kw_pagination_page_2_on_url(driver):
    kw = 'python'

    results = perform_search_by_url(driver,kw=kw,page=2)

    assert len(results) > 0, "Lỗi: Không có dữ liệu trang 2"

    assert_pagination_active(driver, 2)

    assert "kw=python" in driver.current_url

def test_search_kw_empty_on_url(driver):
    kw=''

    results = perform_search_by_url(driver,kw=kw)

    assert_positive(results, kw=None)

def test_search_kw_only_space_on_url(driver):
    kw = '            '

    results = perform_search_by_url(driver,kw=kw)

    assert_positive(results, kw=None)

def test_search_invalid_search_by_on_url(driver):

    results = perform_search_by_url(driver,search_by='abc')

    assert_positive(results, kw=None)

def test_search_invalid_category_on_url(driver):

    results = perform_search_by_url(driver,c_name=99999)

    alert_msg = driver.find_elements(By.CSS_SELECTOR,".container .alert")

    assert len(results) == 0, "Lỗi: Vẫn tìm thấy sách"

    assert len(alert_msg) > 0, "Lỗi: Không có thông báo"

    assert "Không tìm thấy" in alert_msg[0].text