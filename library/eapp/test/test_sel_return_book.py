import time
from selenium.webdriver.common.by import By

from eapp.test.pages.LoginPage import LoginPage
from eapp.test.pages.MyBookPage import MyBookPage
from eapp.test.test_base import driver

USER = ('hung123', '123')


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

    driver.refresh()
    time.sleep(2)

    elements = driver.find_elements(*MyBookPage.REQUESTED_BADGE)
    assert len(elements) > 0
    assert elements[0].is_displayed()

def test_return_button_disabled_after_request(driver):
    page = login_and_open(driver)

    page.click_return_book()
    time.sleep(2)

    page.confirm_swal()
    time.sleep(2)

    page.ok_swal()
    time.sleep(2)

    driver.refresh()
    time.sleep(2)

    btns = driver.find_elements(*MyBookPage.RETURN_BTN)

    if btns:
        assert not btns[0].is_enabled()
    else:
        assert True