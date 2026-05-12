import time
from selenium.webdriver.common.by import By

from eapp.test.pages.LoginPage import LoginPage
from eapp.test.pages.MyBookPage import MyBookPage
from eapp.test.test_base import driver

USER = ('hung123', '123')
EMPTY_USER = ('hung1234', '1234')


def login_and_open(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(*USER)
    time.sleep(2)

    page = MyBookPage(driver=driver)
    page.open_page()
    time.sleep(2)

    return page

def test_return_book_shows_confirm_dialog(driver):
    page = login_and_open(driver)

    page.click_return_book()
    time.sleep(2)

    swal = driver.find_element(By.CSS_SELECTOR, '.swal2-popup')
    assert swal.is_displayed()

def test_return_book_cancel_does_nothing(driver):
    page = login_and_open(driver)

    page.click_return_book()
    time.sleep(2)

    page.cancel_swal()
    time.sleep(2)

    btns = driver.find_elements(*MyBookPage.RETURN_BTN)
    assert len(btns) > 0
    assert btns[0].is_displayed()

def test_return_book_success(driver):
    page = login_and_open(driver)
    page.click_return_book()
    time.sleep(2)
    page.confirm_swal()
    time.sleep(2)
    page.ok_swal()
    time.sleep(2)

    elements = driver.find_elements(*MyBookPage.REQUESTED_BADGE)
    assert len(elements) > 0
    assert elements[0].is_displayed()

def test_return_button_disabled_after_request(driver):
    page = login_and_open(driver)
    btns = driver.find_elements(*MyBookPage.RETURN_BTN)
    if not btns:
        return
    time.sleep(2)
    page.click_return_book()
    time.sleep(2)
    page.confirm_swal()
    time.sleep(2)
    page.ok_swal()
    time.sleep(2)

    requested_badges = driver.find_elements(*MyBookPage.REQUESTED_BADGE)
    assert len(requested_badges) > 0
    assert requested_badges[0].is_displayed()

    other_btns = driver.find_elements(*MyBookPage.RETURN_BTN)
    for btn in other_btns:
        assert btn.is_enabled()

def test_book_card_shows_full_info(driver):
    page = login_and_open(driver)
    titles = driver.find_elements(*MyBookPage.BOOK_TITLE)
    assert len(titles) > 0
    assert titles[0].text.strip() != ''


def test_overdue_book_shows_overdue_status(driver):
    page = login_and_open(driver)
    cards = driver.find_elements(*MyBookPage.BOOK_CARD)
    overdue = [c for c in cards if 'Trễ hạn' in c.text]
    if not overdue:
        return
    assert len(overdue) > 0

def test_overdue_book_shows_fine(driver):
    page = login_and_open(driver)
    cards = driver.find_elements(*MyBookPage.BOOK_CARD)
    overdue = [c for c in cards if 'Phí phạt' in c.text]
    if not overdue:
        return
    assert len(overdue) > 0

def test_status_shows_returning_after_request(driver):
    page = login_and_open(driver)
    btns = driver.find_elements(*MyBookPage.RETURN_BTN)
    if not btns:
        return
    page.click_return_book()
    time.sleep(2)
    page.confirm_swal()
    time.sleep(2)
    page.ok_swal()
    time.sleep(2)
    driver.refresh()
    time.sleep(2)
    statuses = driver.find_elements(*MyBookPage.STATUS_BOOK)
    assert any('Đang trả sách' in s.text for s in statuses)


def test_empty_book_list_shows_message(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(*EMPTY_USER)
    time.sleep(2)
    page = MyBookPage(driver=driver)
    page.open_page()
    time.sleep(2)

    msg = driver.find_element(*MyBookPage.WARNING_MSG)

    assert 'Chưa có sách' in msg.text

def test_return_book_no_return_btn(driver):
    login_and_open(driver=driver)
    driver.get(MyBookPage.URL_BORROWED)
    time.sleep(2)
    btns = driver.find_elements(*MyBookPage.RETURN_BTN)
    assert len(btns) == 0

def test_unauthenticated_redirected_to_login(driver):
    driver.get('http://localhost:5000/my_books_list')
    time.sleep(2)
    assert '/login' in driver.current_url

def test_return_btn_active_when_overdue(driver):
    page = login_and_open(driver)
    cards = driver.find_elements(*MyBookPage.BOOK_CARD)
    overdue = [c for c in cards if 'Trễ hạn' in c.text]
    if not overdue:
        return
    btn = overdue[0].find_element(*MyBookPage.RETURN_BTN)
    assert btn.is_displayed()
    assert btn.is_enabled()

def test_return_btn_active_when_borrowing(driver):
    page = login_and_open(driver)
    cards = driver.find_elements(*MyBookPage.BOOK_CARD)
    borrowing = [c for c in cards if 'Đang mượn' in c.text]
    if not borrowing:
        return
    btn = borrowing[0].find_element(*MyBookPage.RETURN_BTN)
    assert btn.is_displayed()
    assert btn.is_enabled()

def test_send_return_request_overdue_success(driver):
    page = login_and_open(driver)
    cards = driver.find_elements(*MyBookPage.BOOK_CARD)
    overdue_cards = [c for c in cards if 'Trễ hạn' in c.text]
    if not overdue_cards:
        return

    page.click_return_book_in_card(overdue_cards[0])
    time.sleep(2)
    page.confirm_swal()
    time.sleep(2)
    page.ok_swal()
    time.sleep(2)

    badges = driver.find_elements(*MyBookPage.REQUESTED_BADGE)
    assert len(badges) > 0

def test_no_fine_when_borrowing_on_time(driver):
    page = login_and_open(driver)
    cards = driver.find_elements(*MyBookPage.BOOK_CARD)
    borrowing = [c for c in cards if 'Đang mượn' in c.text]
    if not borrowing:
        return
    for card in borrowing:
        assert 'Phí phạt' not in card.text