from selenium.webdriver.common.by import By

from eapp.test.pages.AdminApproveRequestPage import AdminApproveRequestPage
from eapp.test.pages.LoginPage import LoginPage
from eapp.test.test_base import driver
import time

from eapp.test.pages.MyBookPage import MyBookPage

ADMIN = ('admin', '123456')
USER = ('hung123', '123')

def login_and_send_return_book(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(*USER)
    time.sleep(2)

    page = MyBookPage(driver=driver)
    page.open_page()
    time.sleep(2)

    btns = driver.find_elements(*MyBookPage.RETURN_BTN)
    if btns:
        page.click_return_book()
        time.sleep(2)
        page.confirm_swal()
        time.sleep(2)
        page.ok_swal()
        time.sleep(2)

    driver.delete_all_cookies()
    time.sleep(2)

def login_as_admin_and_open_approve_page(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(*ADMIN)
    time.sleep(2)

    page = AdminApproveRequestPage(driver=driver)
    page.open_page()
    time.sleep(2)
    return page

def test_admin_open_approve_page(driver):
    page = login_as_admin_and_open_approve_page(driver)
    assert 'approve_request_view' in driver.current_url

def test_non_admin_open_approve_page(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(*USER)

    time.sleep(2)
    driver.get(AdminApproveRequestPage.URL)
    msg = driver.find_element(*AdminApproveRequestPage.ERROR_MSG)
    assert 'approve_request_view' not in driver.current_url
    assert 'không có quyền' in msg.text

def test_authenticated_redirect_page(driver):
    driver.get(AdminApproveRequestPage.URL)
    time.sleep(2)
    assert 'login' in driver.current_url

def test_table_has_approve_and_reject_buttons(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows:
        return

    assert len(driver.find_elements(*AdminApproveRequestPage.APPROVE_BTN)) > 0
    assert len(driver.find_elements(*AdminApproveRequestPage.REJECT_BTN)) > 0


def test_table_row_has_9_columns(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows:
        return

    cols = rows[0].find_elements(By.TAG_NAME, 'td')
    assert len(cols) == 9

def test_approve_btn_shows_confirm_dialog(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows:
        return

    page.click_approve()
    time.sleep(2)

    swal = driver.find_element(By.CSS_SELECTOR, '.swal2-popup')
    assert swal.is_displayed()


def test_approve_cancel_keeps_table_row(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows_before = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows_before:
        return

    page.click_approve()
    time.sleep(2)
    page.cancel_swal()
    time.sleep(2)

    rows_after = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    assert len(rows_after) == len(rows_before)


def test_approve_success_row_removed(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows_before = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows_before:
        return
    count_before = len(rows_before)

    page.click_approve()
    time.sleep(2)
    page.confirm_swal()
    time.sleep(2)
    page.ok_swal()
    time.sleep(3)

    rows_after = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    assert len(rows_after) < count_before

def test_reject_btn_shows_confirm_dialog(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows:
        return

    page.click_reject()
    time.sleep(2)

    swal = driver.find_element(By.CSS_SELECTOR, '.swal2-popup')
    assert swal.is_displayed()


def test_reject_cancel_keeps_table_row(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows_before = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows_before:
        return

    page.click_reject()
    time.sleep(2)
    page.cancel_swal()
    time.sleep(2)

    rows_after = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    assert len(rows_after) == len(rows_before)


def test_reject_success_row_removed(driver):
    login_and_send_return_book(driver)
    page = login_as_admin_and_open_approve_page(driver)

    rows_before = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    if not rows_before:
        return
    count_before = len(rows_before)

    page.click_reject()
    time.sleep(2)
    page.confirm_swal()
    time.sleep(2)
    page.ok_swal()
    time.sleep(3)

    rows_after = driver.find_elements(*AdminApproveRequestPage.TABLE_ROWS)
    assert len(rows_after) < count_before