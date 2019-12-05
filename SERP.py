import time
import sys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import wait as Wait
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup


def magenta(text):
    print('\033[35m', text, '\033[0m', sep='')


class SeleniumCtrl:

    def __init__(self):

        options = Options()
        options.add_argument('-headless')
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        cap['loggingPrefs'] = {'browser': 'ALL'}

        '''INSERT YOUR PROFILE PATH!!'''
        # profile = webdriver.FirefoxProfile("your path to/profile") # here it goes a firefox profile, setting up a saved profile is the best option

        browser = webdriver.Firefox(executable_path=r"geckodriver")
        self.browser = browser

    def go_to_page(self, my_url):
        driver = self.browser
        driver.get(my_url)

    # it starts the program in Google page for search and perform search for keywords or address
    def search_with_google(self, my_search_query):
        driver = self.browser
        driver.get("https://www.google.com")
        google_bar = driver.find_element_by_css_selector(".gLFyf")
        google_bar.send_keys(str(my_search_query).replace("b'", "").replace("'", ""))
        google_bar.send_keys(Keys.ENTER)

        # get rid of privacy contract with google (it would block navigation)

    def get_rid_of_contract(self):
        time.sleep(5)
        driver = self.browser
        driver_list = [driver]
        for driver in driver_list:
            driver.get(
                "https://consent.google.com/ui/?continue=https://www.google.com/&origin=https://www.google.com&if=1&gl=IT&hl=it&pc=s")
            not_loaded = True
            # print("check before while")

            while not_loaded:
                try:
                    Wait(driver, 1).until(
                        lambda browsed: browsed.find_element_by_css_selector('#yDmH0d').is_displayed())
                    if driver.find_element_by_css_selector('#yDmH0d'):
                        # print("page loaded")
                        not_loaded = False
                    else:
                        print("page not loaded")
                        not_loaded = True
                except:
                    print("into except for loading page_5")
                    not_loaded = True

            my_magic_button = driver.find_element_by_css_selector("#agreeButton")
            my_page_body = driver.find_element_by_css_selector("body")
            my_page_body.send_keys(Keys.END)
            time.sleep(2)
            my_magic_button.click()
            time.sleep(2)

        return False

    def get_source(self):
        driver = self.browser
        my_raw_source = driver.page_source
        return my_raw_source

    def wait_for_page_loaded(self):
        try:
            Wait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "brs"))
            )
        except TimeoutException as e:
            print(e, "connection takes too long", file=sys.stderr)
            driver.quit_driver()

    def go_to_next_serp_page(self, parsed_html):
        next_a = parsed_html.find("a", id="pnnext")
        self.browser.get(f"https://www.google.com{next_a['href']}")
        self.wait_for_page_loaded()
        parsed_html = BeautifulSoup(self.browser.page_source, features="lxml")
        h3_list = parsed_html.find_all("h3")
        return parsed_html, h3_list

    def quit_driver(self):
        print("closing application...")
        self.browser.quit()


if __name__ == "__main__":
    driver = SeleniumCtrl()
    driver.get_rid_of_contract()
    print("please insert a search keyword(s) or an url")
    my_url = input()
    print("please insert the specific string you're looking for into the results")
    my_key = input()
    driver.search_with_google(my_url)

    # now it waits for page loading using selenium proper method
    driver.wait_for_page_loaded()

    # here it starts processing the results
    page = driver.get_source()

    # parse in beautiful soup
    soup = BeautifulSoup(page, features="lxml")
    my_h3 = soup.find_all("h3")

    '''ATM it processes still only ONE SERP page: the first'''
    result = []

    # TODO: add a better way to store collected data: [number in SERP, {site tile: http link}]
    # TODO: save retrivied results into a .csv file with Pandas
    # TODO: create a config.cfg file where storing the default number of SERP's page to parse and other useful defaults (as the max seconds to wait for loading a page)
    # TODO: create a better method to display colored results in print. For info: https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python

    page_to_parse = 10 # it must replaced with param got from command line or from config.cfg

    while page_to_parse >= 1:

        for item in my_h3:
            if item.parent.name == "a":
                if item and item.get_text():
                    a_tag = item.parent
                    result.append({item.get_text(): a_tag["href"]})
            else:
                if item and item.get_text():
                    result.append({item.get_text(): "NO LINK AVAILABLE"})

        # print results in terminal: saving in CSV yet to be implemented
        counter = 0
        if page_to_parse <= 1:
            for elem in result:
                if my_key in str(elem.values()): # search for matching string in found values (the http links)
                    make_evident = True
                    counter += 1
                else:
                    make_evident = False

                if make_evident:
                    magenta(elem)
                else:
                    print(elem)

            print(f"\n{counter} - number of matching entries\n")

        page_to_parse -= 1
        # here switch to next SERP page
        soup, my_h3 = driver.go_to_next_serp_page(soup)

    driver.quit_driver()






