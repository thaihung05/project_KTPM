from eapp.test.pages.LoginPage import LoginPage
from eapp.test.test_base import driver

TEST_USER = ('hung123','123')
TEST_ADMIN = ('admin', '123456')

def test_login_success(driver):
    page = LoginPage(driver)
    page.open_page()
    page.login(*TEST_USER)
    assert '/login' not in driver.current_url

def test_login_wrong_password(driver):
    page = LoginPage(driver)
    page.open_page()
    page.login('user1', 'saimatkhau')

    assert '/login' in driver.current_url
    error = page.find(*page.ERROR_MESSAGE)
    assert error.is_displayed()