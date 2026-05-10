from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




class BasePage:
    BASE_URL = "http://localhost:5000"



    def __init__(self, driver):
        self.driver = driver

    def open(self, path):
        self.driver.get(self.BASE_URL + path)

    def find(self, by, value):
        return self.driver.find_element(by=by, value=value)

    def finds(self, by, value):
        return self.driver.find_elements(by=by, value=value)

    def typing(self, by, value, text):
        e = self.find(by=by, value=value)
        e.send_keys(text)

    def click(self, by, value):
        e = self.find(by=by, value=value)
        e.click()

    def wait_for_swal(self, timeout = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.swal2-popup'))
        )

    def confirm_swal(self, timeout = 10):
        self.wait_for_swal(timeout)
        self.click(By.CSS_SELECTOR, '.swal2-confirm')

    def cancel_swal(self, timeout = 10):
        self.wait_for_swal(timeout)
        self.click(By.CSS_SELECTOR, '.swal2-cancel')

    def ok_swal(self, timeout = 10):
        self.wait_for_swal(timeout)
        self.click(By.CSS_SELECTOR, '.swal2-confirm.swal2-styled')

    def get_swal_message(self, timeout = 10):
        self.wait_for_swal(timeout)
        return str(self.find(By.ID, 'swal2-html-container').text)