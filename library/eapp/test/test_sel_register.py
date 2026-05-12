import time

import pytest

from eapp.test.pages.LoginPage import LoginPage
from eapp.test.pages.RegisterPage import RegisterPage
from eapp.test.register_helper import register_user
from eapp.test.test_base import driver
from eapp.test.test_sel_return_book import login_and_open

USER = ('test1', '123', '123', 'test')
USER_WRONG_CONFIRM = ('test2', '123', '12', 'Test Wrong Confirm Pass')
USER_NAME_NULL = ('test3', '123', '12', '')
USER_USERNAME_NULL = ('', '123', '123', 'Test username null')


def test_register_success(driver):
    page = register_user(driver=driver, user=USER)
    assert '/login' in driver.current_url
    time.sleep(2)
    page = LoginPage(driver=driver)
    page.login(username='test1', password='123')
    time.sleep(2)
    assert '/books' in driver.current_url


def test_register_username_already_exists(driver):
    page = register_user(driver=driver, user=USER)
    time.sleep(1)
    msg = page.get_alert_msg()
    assert 'Username này đã được đăng ký' in msg


def test_register_wrong_confirm_password(driver):
    page = register_user(driver=driver, user=USER_WRONG_CONFIRM)
    time.sleep(1)
    msg = page.get_alert_msg()
    assert 'Mật khẩu không khớp' in msg


@pytest.mark.parametrize(
    'username,password,confirm_password,name',
    [
        ('testNameNull', '123', '123', ''),
        ('testPassNull', '', '123', 'Test'),
        ('testConfirmPassNull', '123', '', 'Test'),
        ('', '123', '123', 'Test No UserName')
    ]
)
def test_register_missing_required_field(driver,username,password,confirm_password,name):
    USER_TEMP=(username,password,confirm_password,name)
    page = RegisterPage(driver)
    page.open_page()

    driver.execute_script(
        "document.querySelectorAll('input[required]').forEach(el => el.removeAttribute('required'));"
    )

    page.register(*USER_TEMP)
    time.sleep(1)
    assert '/register' in driver.current_url
    msg = page.get_alert_msg()
    assert 'Vui lòng điền đầy đủ thông tin' in msg
