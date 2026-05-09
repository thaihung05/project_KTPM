from selenium.webdriver.common.by import By
from eapp.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = "http://127.0.0.1:5000/login"
    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    LOGIN_BTN = (By.CSS_SELECTOR, "button.btn.btn-primary.w-100")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert.alert-danger")

    def open_page(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.click(*self.LOGIN_BTN)
