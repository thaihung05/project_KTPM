from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from eapp.test.pages.BasePage import BasePage
from eapp.test.search_helper import clean_text

class BooksPage(BasePage):
    URL = "http://127.0.0.1:5000/books"
    INPUT_SELECTOR = (By.CSS_SELECTOR, "form > div > input")
    BTN_SELECTOR = (By.CSS_SELECTOR,"form > div > button")
    SELECT_SELECTOR = (By.CSS_SELECTOR,"form > select")
    ITEMS_SELECTOR_CATEGORY = (By.CSS_SELECTOR, ".container div.list-group a.list-group-item")
    BUTTON_PAGE = (By.CSS_SELECTOR,".pagination .page-item .page-link")

    def open_page(self):
        self.driver.get(self.URL)

    def search(self, kw):
        self.typing(*self.INPUT_SELECTOR, kw)
        self.click(*self.BTN_SELECTOR)

    def select_search_type(self, value):
        select_element = self.find(*self.SELECT_SELECTOR)
        select = Select(select_element)
        select.select_by_value(value)

    def click_category(self, category_name):
        categories = self.finds(*self.ITEMS_SELECTOR_CATEGORY)


        for c in categories:
            if clean_text(category_name) in clean_text(c.text):
                c.click()
                return True
        return False

    def click_page(self, page):
        pages = self.finds(*self.BUTTON_PAGE)

        for p in pages:
            if p.text.strip() == str(page):
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", p
                )

                self.driver.execute_script(
                    "arguments[0].click();", p
                )

                return True

        return False
