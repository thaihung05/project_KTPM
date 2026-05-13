import time

import pytest
from selenium.webdriver.common.by import By

from eapp.test.pages.BasePage import BasePage
from eapp.test.pages.BookPage import BookPage
from eapp.test.pages.CartPage import CartPage
from eapp.test.pages.DetailPage import DetailPage
from eapp.test.pages.LoginPage import LoginPage
from eapp.test.test_base import driver

USER_MAIN = ('vanlong01', 'Abc123')
USER_5_BOOKS = ('test5books', '123456')
USER_4_BOOKS = ('test4books', '123456')
USER_1_BOOKS = ('test1books', '123456')
USER_3_BOOKS = ('test3books', '123456')
USER_LOCKED = ('testlocked', '123456')
USER_OVERDUE = ('useroverdue', '123456')
USER_RETURNED_OVERDUE = ('userreturnedoverdue', '123456')
USER_RETURNED_ONTIME = ('userreturnedontime', '123456')
SWAL = (By.CSS_SELECTOR, '.swal2-popup')
CART_COUNTER = (By.CLASS_NAME, 'cart-counter')


def login(driver, user):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login(*user)

    page = BookPage(driver=driver)

    return page


def test_borrow_now_not_login(driver):
    page = BookPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.click_borrow_now_btn()
    time.sleep(1)
    page.click_swal_ok_btn()
    assert '/login' in driver.current_url


def test_cart_borrow_not_login(driver):
    page = BookPage(driver=driver)
    page.open_page()
    driver.implicitly_wait(1)
    page.click_borrow_cart_btn()
    driver.implicitly_wait(1)
    page.click_swal_ok_btn()
    assert '/login' in driver.current_url


def test_redirect_after_login(driver):
    login(driver=driver, user=USER_MAIN)
    time.sleep(1)
    assert '/books' in driver.current_url


def test_borrow_now_success(driver):
    page = login(driver=driver, user=USER_MAIN)
    page.click_borrow_now_btn()

    popup = driver.find_element(*SWAL)
    assert popup.is_displayed()


def test_popup_cart_borrow_success(driver):
    page = login(driver=driver, user=USER_MAIN)
    page.click_borrow_cart_btn()
    msg = page.get_swal_message()
    assert 'đã được thêm vào giỏ hàng' in msg


def test_cart_counter_success(driver):
    page = login(driver=driver, user=USER_MAIN)
    time.sleep(2)
    e = driver.find_element(*CART_COUNTER)
    count = int(e.text)
    page.click_borrow_cart_btn()
    time.sleep(2)
    assert int(e.text) == count + 1


def test_one_book_appears_in_cart(driver):
    page = login(driver=driver, user=USER_MAIN)
    title ='Giáo trình Ngôn ngữ lập trình C++'
    page.click_borrow_cart_btn()
    time.sleep(2)
    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    cart = driver.find_elements(By.CSS_SELECTOR, '#cart-body tr')
    assert len(cart) > 0

    titles_in_cart = [c.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text for c in cart]
    assert title in titles_in_cart


def test_submit_borrow_one_in_cart(driver):
    page = login(driver=driver, user=USER_MAIN)
    page.click_borrow_cart_btn()
    time.sleep(2)
    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    cart = driver.find_elements(By.CSS_SELECTOR, '#cart-body tr')
    assert len(cart) > 0
    page.submit_checkbox()
    page.click_btn_success()
    msg = page.get_swal_message()
    assert 'Mượn sách thành công' in msg


def test_submit_borrow_two_in_cart(driver):
    page = login(driver=driver, user=USER_MAIN)
    time.sleep(1)
    btns = page.finds(*BookPage.BORROW_CART_BTN)

    for btn in btns[:2]:
        btn.click()
        time.sleep(2)

    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    cart = driver.find_elements(By.CSS_SELECTOR, '#cart-body tr')
    assert len(cart) > 0
    page.submit_all_checkboxes()
    page.click_btn_success()
    msg = page.get_swal_message()
    assert 'Mượn sách thành công' in msg


def test_submit_borrow_six_in_cart(driver):
    page = login(driver=driver, user=USER_MAIN)
    driver.execute_script("window.scrollTo(0,400);")
    time.sleep(3)
    btns = page.finds(*BookPage.BORROW_CART_BTN)

    for btn in btns[:6]:
        btn.click()
        time.sleep(2)

    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.submit_all_checkboxes()
    msg = page.get_swal_message()
    assert 'chọn tối đa 5 quyển sách' in msg


def test_borrow_cart_one_active_select_five_books(driver):
    page = login(driver=driver, user=USER_1_BOOKS)
    driver.execute_script("window.scrollTo(0,400);")
    time.sleep(3)
    btns = page.finds(*BookPage.BORROW_CART_BTN)

    for btn in btns[:5]:
        btn.click()
        time.sleep(2)

    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.submit_all_checkboxes()
    page.click_btn_success()
    msg = page.get_swal_message()
    assert 'chỉ được chọn thêm 4 quyển' in msg


def test_borrow_now_five_active(driver):
    page = login(driver=driver, user=USER_5_BOOKS)
    page.click_borrow_now_btn()
    msg = page.get_swal_message()
    assert 'mượn tối đa 5 quyển sách' in msg


def test_cart_borrow_four_active_select_two_books(driver):
    page = login(driver=driver, user=USER_4_BOOKS)
    btns = page.finds(*BookPage.BORROW_CART_BTN)

    for btn in btns[:2]:
        btn.click()
        time.sleep(2)

    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.submit_all_checkboxes()
    page.click_btn_success()
    msg = page.get_swal_message()
    assert 'chỉ được chọn thêm 1 quyển' in msg


def test_borrow_now_with_locked_account(driver):
    page = login(driver=driver, user=USER_LOCKED)
    page.click_borrow_now_btn()
    msg = page.get_swal_message()
    time.sleep(1)
    assert 'bị khóa' in msg


def test_cart_borrow_with_locked_account(driver):
    page = login(driver=driver, user=USER_LOCKED)
    page.click_borrow_cart_btn()
    time.sleep(2)
    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.submit_checkbox()
    page.click_btn_success()
    msg = page.get_swal_message()
    time.sleep(1)
    assert 'bị khóa' in msg


def test_cart_borrow_five_books_with_locked_account(driver):
    page = login(driver=driver, user=USER_LOCKED)
    driver.execute_script("window.scrollTo(0,400);")
    time.sleep(3)
    btns = page.finds(*BookPage.BORROW_CART_BTN)

    for btn in btns[:5]:
        btn.click()
        time.sleep(2)

    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.submit_all_checkboxes()
    page.click_btn_success()
    msg = page.get_swal_message()
    assert 'bị khóa' in msg


def test_borrow_now_with_account_has_overdue(driver):
    page = login(driver=driver, user=USER_OVERDUE)
    page.click_borrow_now_btn()
    msg = page.get_swal_message()
    assert 'có sách quá hạn chưa trả' in msg


def test_cart_borrow_with_account_has_overdue(driver):
    page = login(driver=driver, user=USER_OVERDUE)
    page.click_borrow_cart_btn()
    time.sleep(2)
    page = CartPage(driver=driver)
    page.open_page()
    time.sleep(1)
    page.submit_checkbox()
    page.click_btn_success()
    msg = page.get_swal_message()
    assert 'còn sách quá hạn chưa trả' in msg


def test_out_of_stock_when_login(driver):
    page = login(driver=driver, user=USER_MAIN)
    time.sleep(1)
    out_of_stock_btns = page.get_out_of_stock_btns()
    assert len(out_of_stock_btns) > 0


def test_out_of_stock_when_not_login(driver):
    page = BookPage(driver=driver)
    page.open_page()
    out_of_stock_btns = page.get_out_of_stock_btns()
    assert len(out_of_stock_btns) > 0



def test_out_of_stock_badge_in_detail_page(driver):
    page = DetailPage(driver=driver)
    page.open_page()
    driver.execute_script('window.scrollTo(0,400);')
    time.sleep(1)
    els = page.get_out_of_stock_badges()
    assert len(els) > 0
    for i in range(len(els)):
        assert 'Hết sách' in els[i].text


def test_borrow_now_last_one_then_out_of_stock(driver):
    page = login(driver=driver, user=USER_MAIN)
    driver.execute_script('window.scrollTo(0,1000);')
    time.sleep(3)

    e = page.find(By.CSS_SELECTOR, 'button[onclick="borrowBook(15)"]')
    e.click()

    msg = page.get_swal_message()
    time.sleep(2)
    out_of_stock_btns = page.get_out_of_stock_btns()
    assert 'Mượn thành công' in msg

    assert len(out_of_stock_btns) > 0


def test_cart_borrow_last_one_then_out_of_stocks(driver):
    page = login(driver=driver, user=USER_3_BOOKS)
    driver.execute_script('window.scrollTo(0,1000);')
    time.sleep(1)
    out_of_stock_btns_before = page.get_out_of_stock_btns()
    e = driver.find_element(By.CSS_SELECTOR,
                            'button[onclick="addToCart(14, \'Quản lý dự án phần mềm theo Agile/Scrum\')"]')
    e.click()
    time.sleep(2)

    cartPage = CartPage(driver=driver)
    cartPage.open_page()
    time.sleep(1)
    cartPage.submit_checkbox()
    cartPage.click_btn_success()
    time.sleep(2)

    page.open_page()
    driver.execute_script('window.scrollTo(0,1000);')
    time.sleep(1)
    out_of_stock_btns_after = page.get_out_of_stock_btns()
    assert len(out_of_stock_btns_after) > len(out_of_stock_btns_before)



def test_borrow_after_overdue_returned(driver):
    page = login(driver=driver, user=USER_RETURNED_OVERDUE)
    time.sleep(1)

    page.click_borrow_now_btn()
    msg = page.get_swal_message()
    assert 'Mượn thành công' in msg



def test_borrow_after_on_time_returned(driver):
    page = login(driver=driver, user=USER_RETURNED_ONTIME)
    time.sleep(1)

    page.click_borrow_now_btn()
    msg = page.get_swal_message()
    assert 'Mượn thành công' in msg


def test_cart_borrow_after_overdue_returned(driver):
    page = login(driver=driver, user=USER_RETURNED_OVERDUE)
    page.click_borrow_cart_btn()
    time.sleep(2)

    cartPage = CartPage(driver=driver)
    cartPage.open_page()
    time.sleep(1)
    cartPage.submit_checkbox()
    cartPage.click_btn_success()

    msg = page.get_swal_message()
    assert 'Mượn sách thành công' in msg


def test_cart_borrow_after_on_time_returned(driver):
    page = login(driver=driver, user=USER_RETURNED_ONTIME)
    page.click_borrow_cart_btn()
    time.sleep(2)

    cartPage = CartPage(driver=driver)
    cartPage.open_page()
    time.sleep(1)
    cartPage.submit_checkbox()
    cartPage.click_btn_success()

    msg = page.get_swal_message()
    assert 'Mượn sách thành công' in msg

def test_confirm_empty_cart(driver):
    page=login(driver=driver, user=USER_MAIN)
    time.sleep(1)
    cartPage = CartPage(driver=driver)
    cartPage.open_page()
    cartPage.click_btn_success()
    msg = page.get_swal_message()
    assert 'chưa chọn quyển nào để mượn' in msg
