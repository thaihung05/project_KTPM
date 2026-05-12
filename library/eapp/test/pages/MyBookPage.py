import time

from selenium.webdriver.common.by import By

from eapp.test.pages.BasePage import BasePage


class MyBookPage(BasePage):
    URL = 'http://localhost:5000/my_books_list'
    URL_BORROWED = 'http://localhost:5000/my_borrowed_books'
    URL_BORROWING = 'http://localhost:5000/my_borrowing_books'


    RETURN_BTN = (By.CSS_SELECTOR, '.btn-danger.btn-sm')
    REQUESTED_BADGE = (By.CSS_SELECTOR, '.btn-secondary.btn-sm')
    BOOK_TITLE = (By.CSS_SELECTOR, '.card-title')
    STATUS_BOOK = (By.CSS_SELECTOR, '.card-body p.card-text.text-dark')
    BOOK_CARD = (By.CSS_SELECTOR, '.book-card-frame')
    WARNING_MSG = (By.CSS_SELECTOR, '.alert.alert-warning')

    def open_page(self):
        self.driver.get(self.URL)

    def click_return_book(self):
        self.driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        e = self.driver.find_element(*self.RETURN_BTN)
        e.click()

    def click_return_book_in_card(self, card):
        self.driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        card.find_element(*self.RETURN_BTN).click()