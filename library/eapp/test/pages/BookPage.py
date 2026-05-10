import time

from eapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class BookPage(BasePage):
    URL="http://127.0.0.1:5000/books"

    OUT_OF_STOCK_BTN = (By.CSS_SELECTOR,'button.btn-secondary[disabled]')
    BORROW_NOW_BTN = (By.CSS_SELECTOR,'.book-card-frame button.btn-primary')
    BORROW_CART_BTN = (By.CSS_SELECTOR, '.book-card-frame button.btn-outline-primary')
    SWAL_OK_BTN = (By.CSS_SELECTOR,'.swal2-actions button.swal2-confirm')
    SWAL_CANCEL_BTN = (By.CSS_SELECTOR,'.swal2-actions button.swal2-cancel')
    def open_page(self):
        self.driver.get(self.URL)


    def click_borrow_now_btn(self):
        self.driver.implicitly_wait(1)
        e = self.driver.find_element(*self.BORROW_NOW_BTN)
        e.click()

    def click_borrow_cart_btn(self):
        self.driver.implicitly_wait(1)
        e = self.driver.find_element(*self.BORROW_CART_BTN)
        e.click()

    def click_swal_ok_btn(self):
        self.driver.implicitly_wait(1)
        e = self.driver.find_element(*self.SWAL_OK_BTN)
        e.click()

    def click_swal_cancel_btn(self):
        self.driver.implicitly_wait(1)
        e = self.driver.find_element(*self.SWAL_CANCEL_BTN)
        e.click()

    def get_out_of_stock_btns(self):
        return self.driver.find_elements(*self.OUT_OF_STOCK_BTN)

    def get_out_of_stock_btn(self):
        return self.driver.find_element(*self.OUT_OF_STOCK_BTN)


