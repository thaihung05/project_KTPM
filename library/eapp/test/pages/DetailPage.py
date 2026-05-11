from selenium.webdriver.common.by import By

from eapp.test.pages.BasePage import BasePage


class DetailPage(BasePage):
    URL='http://127.0.0.1:5000/'

    OUT_OF_STOCK_BADGE = (By.CSS_SELECTOR,'span.text-danger')

    def open_page(self):
        return self.driver.get(self.URL)


    def get_out_of_stock_badges(self):
        return self.driver.find_elements(*self.OUT_OF_STOCK_BADGE)
