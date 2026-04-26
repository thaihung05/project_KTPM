import time

from selenium.webdriver.common.by import By

from eapp.test.pages.BasePage import BasePage


class MyBookPage(BasePage):
    URL = 'http://localhost:5000/my_books_list'

    RETURN_BTN = (By.CSS_SELECTOR, '.btn-danger.btn-sm')
    REQUESTED_BADGE = (By.CSS_SELECTOR, '.btn-secondary.btn-sm')

    def open_page(self):
        self.driver.get(self.URL)

    def click_return_book(self):
        self.driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        e = self.driver.find_element(*self.RETURN_BTN)
        e.click()