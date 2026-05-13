import time
import unicodedata
from selenium.webdriver.common.by import By
from urllib.parse import urlencode


def perform_search(driver, kw=None, c_name=None, search_by=None,page=None, open_page=True):
    from eapp.test.pages.BooksPage import BooksPage

    books = BooksPage(driver)
    if open_page:
        books.open_page()

    if c_name:
        books.click_category(c_name)
        time.sleep(1)

    if search_by:
        books.select_search_type(search_by)

    if kw is not None:
        books.search(kw)
        time.sleep(1)
        driver.implicitly_wait(1)

    if page:
        books.click_page(page)
        time.sleep(1)

    driver.implicitly_wait(1)

    results = driver.find_elements(By.CSS_SELECTOR, '.book-card-frame')
    return results

def perform_search_by_url(driver, kw=None, c_name=None, search_by=None,page=None):
    params = {}

    if kw is not None:
        params["kw"] = kw

    if search_by is not None:
        params["search_by"] = search_by

    if c_name is not None:
        params["category_id"] = c_name

    if page is not None:
        params["page"] = page

    query_string = urlencode(params)

    url = f"http://127.0.0.1:5000/books?{query_string}"

    driver.get(url)

    return perform_search(driver, open_page=False)


def clean_text(text):
    if not text:
        return ""

    text = text.lower()
    text = text.strip()
    nfkd_form = unicodedata.normalize('NFKD', text)
    result = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    return result.replace('đ', 'd')


def assert_positive(results, kw, search_by='title'):
    assert len(results) > 0, f"Lỗi: Không tìm thấy '{kw}'"

    if kw:
        for r in results:
            if search_by == 'author':
                target_text = r.find_element(By.CSS_SELECTOR, '.card-text').text
            else:
                target_text = r.find_element(By.CSS_SELECTOR, '.card-title').text
            clean_kw = clean_text(kw)
            clean_target = clean_text(target_text)

            assert clean_kw in clean_target, f"Lỗi: '{kw}' không khớp với '{target_text}'"

def assert_negative(driver, results, kw):
    assert len(results) == 0, "Lỗi: Tìm thấy sách!"

    alert_msg = driver.find_elements(By.CSS_SELECTOR, ".container .alert")

    assert len(alert_msg) > 0, "Lỗi: Không thấy thông báo trên màn hình!"

    if len(kw.strip()) >= 2:
        assert "Không tìm thấy" in alert_msg[0].text
    else:
        assert "Vui lòng nhập từ 2 ký tự trở lên để tìm kiếm sách!!!" in alert_msg[0].text

def assert_category_active(driver, c_name):
    active_cate = driver.find_element(By.CSS_SELECTOR, ".list-group-item.text-primary.bg-light").text
    assert c_name.lower() in active_cate.lower(), f"Lỗi: Thể loại '{c_name}' chưa được bật!"

def assert_pagination_active(driver, page):
    active_page = driver.find_element(By.CSS_SELECTOR, ".page-item.active")
    actual_page = active_page.text.strip()

    assert actual_page == str(page), \
        f"Lỗi: Trang hiện tại là {actual_page}, không phải {page}"

    assert f"page={page}" in driver.current_url, f"Lỗi: URL không chứa page={page}"
