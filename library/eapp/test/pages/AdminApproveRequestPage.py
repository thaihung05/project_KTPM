import time

from selenium.webdriver.common.by import By

from eapp.test.pages.BasePage import BasePage

class AdminApproveRequestPage(BasePage):
    URL = 'http://localhost:5000/admin/approve_request_view'

    APPROVE_BTN = (By.CSS_SELECTOR, '.btn.btn-success.btn-sm')
    REJECT_BTN = (By.CSS_SELECTOR, '.btn.btn-danger.btn-sm')
    TABLE_ROWS = (By.CSS_SELECTOR, 'tbody tr')
    EMPTY_MSG = (By.CSS_SELECTOR, '.alert.alert-warning')
    ERROR_MSG = (By.CSS_SELECTOR, '.alert.alert-danger')

    def open_page(self):
        self.driver.get(self.URL)

    def click_approve(self):
        e = self.find(*self.APPROVE_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", e)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", e)

    def click_reject(self):
        e = self.find(*self.REJECT_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", e)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", e)