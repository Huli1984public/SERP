import time
import sys
from random import randint
import json
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import wait as Wait
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import pandas as pd

from bs4 import BeautifulSoup


def magenta(text):
    print('\033[35m', text, '\033[0m', sep='')


def get_rest(random_val=13, divisore=1):
    value = randint(0, random_val)
    time.sleep(base_of_random + int(value/divisore))


class SeleniumCtrl:

    def __init__(self, headless, gecko):

        options = Options()
        options.add_argument('-headless')
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        cap['loggingPrefs'] = {'browser': 'ALL'}

        '''INSERT YOUR PROFILE PATH!!'''
        # profile = webdriver.FirefoxProfile("your path to/profile") # here it goes a firefox profile, setting up a saved profile is the best option
        user_agent = UserAgent()
        user_agent = user_agent.random
        print(f"{user_agent}, user agent")
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", f"{user_agent}")

        if headless:
            browser = webdriver.Firefox(capabilities=cap, options=options, firefox_profile=profile, executable_path=gecko)
        else:
            browser = webdriver.Firefox(firefox_profile=profile, executable_path=gecko)

        self.browser = browser

    def go_to_page(self, my_url):
        driver = self.browser
        driver.get(my_url)

    # it starts the program in Google page for search and perform search for keywords or address
    def search_with_google(self, my_search_query):
        driver = self.browser
        driver.get("https://www.google.com")
        try:
            google_bar = driver.find_element_by_css_selector(".gLFyf")
        except NoSuchElementException:
            self.wait_for_page_loaded(time=3, obj="fsr")

        google_bar.send_keys(str(my_search_query).replace("b'", "").replace("'", ""))
        google_bar.send_keys(Keys.ENTER)

    def get_url(self):
        return self.browser.current_url

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
            try:
                my_magic_button.click()
            except ElementNotInteractableException:
                time.sleep(5)
                my_page_body.send_keys(Keys.END)
                try:
                    my_magic_button.click()
                except ElementNotInteractableException as e:
                    print(e)
                    print("Critical error line 110")
                    driver.quit()
            time.sleep(2)

        return False

    def get_source(self):
        driver = self.browser
        my_raw_source = driver.page_source
        return my_raw_source

    def wait_for_page_loaded(self, time=10, obj="foot"):
        try:
            Wait(self.browser, time).until(
                EC.presence_of_element_located((By.ID, obj))
            )
        except TimeoutException as e:
            try:
                Wait(self.browser, time).until(
                    EC.presence_of_element_located((By.ID, "brs"))
                )
            except TimeoutException as e:
                print(e, "connection takes too long", file=sys.stderr)
                # driver.quit_driver()

    def go_to_next_serp_page(self, parsed_html, remains, time=10):
        next_a = parsed_html.find("a", id="pnnext")
        try:
            self.browser.get(f"https://www.google.com{next_a['href']}")
            self.wait_for_page_loaded(time)
            parsed_html = BeautifulSoup(self.browser.page_source, features="lxml")
            h3_list = parsed_html.find_all("h3")
            return parsed_html, h3_list, remains
        except TypeError as e:
            print(f'End of pages reached')
            remains = 0
            return parsed_html, [], remains

    def quit_driver(self):
        print("closing application...")
        self.browser.quit()


if __name__ == "__main__":

    start_time = time.time()

    with open("config.json", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(None, columns=['google search', 'key', 'page', "abs Pos", 'title', 'link'])

    print("getting urls from configuration file: edit it to add or remove google search keywords")
    my_url_list = data["urls"]
    lazy_search = data["lazy mode"]
    base_of_random = data["default wait"]
    headless = data["headless"]
    geckodriver = data["geckodriver"]

    for my_url in my_url_list:

        driver = SeleniumCtrl(headless, geckodriver)
        print("opening browser")
        driver.get_rid_of_contract()

        get_rest(random_val=10)
        driver.search_with_google(my_url)

        seconds = int(data["max_time_to_wait"])

        # now it waits for page loading using selenium proper method
        driver.wait_for_page_loaded(time=seconds)
        url_now = driver.get_url()

        # here it starts processing the results
        page = driver.get_source()

        # parse in beautiful soup
        soup = BeautifulSoup(page, features="lxml")
        my_h3 = soup.find_all("h3")

        key_list = data["key_list"]
        page_to_parse = data["page_to_parse"]

        page_number = 1
        absolute_position = 1

        for my_key in key_list:
            print(my_url, my_key, key_list)
            get_rest(random_val=8)
            while page_to_parse >= 1:
                for item in my_h3:
                    if item.parent.name == "a":
                        if item and item.get_text():
                            a_tag = item.parent
                            absolute_position += 1

                            # create Pandas Series
                            if my_key in str(a_tag['href']):
                                # create Pandas Series
                                serie = pd.Series({'google search': my_url, 'key': my_key, 'page': page_number,
                                                   'abs Pos': absolute_position, 'title': item.get_text(),
                                                   'link': a_tag[
                                                       'href']})  # at this point it still lacks of absolute index.

                                # inject Series into Pandas df
                                df = df.append(serie, ignore_index=True)

                                if lazy_search == 1:
                                    page_to_parse = 0
                    else:
                        if item and item.get_text():
                            absolute_position += 1

                page_number += 1
                page_to_parse -= 1

                # here switch to next SERP page
                soup, my_h3, page_to_parse = driver.go_to_next_serp_page(soup, page_to_parse, time=seconds)

            # reset the loops value to parse the next key
            if page_to_parse <= 1:
                driver.go_to_page(url_now)
                driver.wait_for_page_loaded(time=seconds)
                page = driver.get_source()

                # parse in beautiful soup
                soup = BeautifulSoup(page, features="lxml")
                my_h3 = soup.find_all("h3")
                page_number = 1
                absolute_position = 1
                page_to_parse = data["page_to_parse"]
                get_rest(random_val=10, divisore=2)
                driver.quit_driver()

    # quit driver as job is done - eventually prompt for further researches
    df.to_csv('keypos.csv')
    with pd.option_context('display.max_columns', None):
        print(df)
    if driver:
        driver.quit_driver()
    print("--- %s seconds ---" % (time.time() - start_time))






