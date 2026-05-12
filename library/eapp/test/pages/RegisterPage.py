from selenium.webdriver.common.by import By

from eapp.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = 'http://127.0.0.1:5000/register'

    USERNAME=(By.ID,'username')
    PASSWORD =(By.ID,'password')
    NAME = (By.ID, 'name')
    CONFIRM=(By.ID,'confirm')
    REGISTER_BTN=(By.CSS_SELECTOR,'button.btn-primary')
    ALERT = (By.CLASS_NAME,'alert')

    def open_page(self):
        self.driver.get(self.URL)

    def register(self, username, password,confirm,name):
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.typing(*self.CONFIRM, confirm)
        self.typing(*self.NAME, name)
        self.click(*self.REGISTER_BTN)

    def get_alert_msg(self):
        return str(self.find(*self.ALERT).text)