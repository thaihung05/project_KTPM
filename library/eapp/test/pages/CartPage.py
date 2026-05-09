import time

from eapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class CartPage(BasePage):
    URL='http://127.0.0.1:5000/cart'

    BTN_DELETE = (By.CSS_SELECTOR, 'button.btn-danger.btn-sm')
    BTN_SUCCESS = (By.CSS_SELECTOR, 'button.btn-success')
    CHECKBOX = (By.CSS_SELECTOR,'input.book-sel')

    def open_page(self):
        self.driver.get(self.URL)

    def click_btn_delete(self):
        btn=self.driver.find_element(*self.BTN_DELETE)
        btn.click()

    def click_all_btn_delete(self):
        btns=self.driver.find_elements(*self.BTN_DELETE)
        for btn in btns:
            btn.click()

    def click_btn_success(self):
        btn=self.driver.find_element(*self.BTN_SUCCESS)
        btn.click()

    def submit_checkbox(self):
        chb=self.driver.find_element(*self.CHECKBOX)
        chb.click()

    def submit_all_checkboxes(self):
        checkboxes= self.driver.find_elements(*self.CHECKBOX)
        for checkbox in checkboxes:
            if not checkbox.is_selected():
                checkbox.click()



