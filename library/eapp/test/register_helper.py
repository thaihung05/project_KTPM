from eapp.test.pages.RegisterPage import RegisterPage
from eapp.test.test_base import driver

def register_user(driver,user):
    page = RegisterPage(driver=driver)
    page.open_page()
    page.register(*user)

    return page