from selenium import webdriver
import time
import utils
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pandas as pd

from config import config


class Blast:
    s = Service("./geckodriver")

    def __init__(self, profile='profile.ini'):
        self.__options = Options()
        self.__options.add_argument("-profile")
        self.__options.add_argument(config(profile)['profile_path'])
        self.__driver = webdriver.Firefox(service=Blast.s, options=self.__options)
        self.wait = WebDriverWait(self.__driver, 45)
        self.active = False
        self.fwd_number = 1
        self.pause = 0.5
        self.contact = ['Father']
        self.temp = []
        self.report = pd.DataFrame()
        self.xpath = {
            'pane_side': '//div[@id="pane-side"]',
            'main': '//div[@id="main"]',
            'messages': '//div[@aria-label="Message list. Press right arrow key on a message to open message context menu."]/div',
            'msg_option': '//span[@data-testid="down-context"]/parent::*/parent::*',
            'forward': '//div[@aria-label="Forward message"]',
            'fwd_btn': '//button[@title="Forward message"]',
            'fwds_btn': '//button[@title="Forward messages"]',
            'search_fwd': '//div[@role="textbox"]',
            'send': '//div[@role="button"]',
            'checkbox_fwd': '//div[@data-testid="visual-checkbox"]',
            'search_name': '//div[@title="Search input textbox"]',
            'active_sign': '//span[@data-testid="alert-notification"]'
        }
        self.count = 0

    # Common commands
    def klik(self, xpath):
        self.clickable(xpath)
        self.__driver.find_element(By.XPATH, xpath).click()

    def cek_n_klik(self, xpath, t):
        self.doesexist(xpath, t)
        self.__driver.find_element(By.XPATH, xpath).click()

    def access(self, url='https://web.whatsapp.com/'):
        self.__driver.get(url)

    # Specific commands
    def isactive(self):
        try:
            self.doesexist(self.xpath['active_sign'], t=3)
            return True
        except TimeoutException:
            return False

    def search_name(self, name='Mother'):
        search = self.__driver.find_element(By.XPATH, self.xpath['search_name'])
        search.clear()
        search.send_keys(name)

    def choose_name_or_group(self, name='CHECK'):
        self.klik(f'//span[@title="{name}"]')

    def click_msg_option(self):
        main_panel = self.__driver.find_element(By.XPATH, self.xpath['main'])
        elems = main_panel.find_elements(By.XPATH, self.xpath['messages'])
        child = elems[-1].find_element(By.TAG_NAME, "div")
        ActionChains(self.__driver).move_to_element(child).perform()  # hover over
        time.sleep(1)
        elems[-1].find_element(By.XPATH, self.xpath['msg_option']).click()
        # self.klik(self.xpath['msg_option'])

    # Forward message(s)
    def click_fwd_msg(self):
        self.klik(self.xpath['forward'])

    def click_msg_to_fwd(self, n=1):
        checkboxes = self.__driver.find_elements(By.XPATH, self.xpath['checkbox_fwd'])
        self.fwd_number = n
        if n > 1:
            for i in range(1, n):
                checkboxes[-1 - i].click()
        else:
            pass

    def click_fwd_btn(self):
        if self.fwd_number == 1:
            self.klik(self.xpath['fwd_btn'])
        else:
            self.klik(self.xpath['fwds_btn'])

    def fill_click_target_fwd(self, name='Father'):
        search = self.__driver.find_element(By.XPATH, self.xpath['search_fwd'])
        search.send_keys(name)
        time.sleep(self.pause)
        try:
            self.cek_n_klik(f'//span[@title="{name}"]', t=3)
            self.temp.append(1)
            self.count += 1
        except ElementNotInteractableException:
            print(f"Can't click {name}!")
        except TimeoutException:
            print(f"Can't find {name}!")
            self.temp.append(0)
        finally:
            search.clear()

    def send_fwd(self):
        self.klik(self.xpath['send'])

    def forward(self, source, n, targets: list):
        self.report = pd.DataFrame({'name': targets})
        self.temp = []
        all_target = utils.list_partition(targets)
        for subtarget in all_target:
            self.looptilactive()
            self.choose_name_or_group(source)
            time.sleep(self.pause)
            self.click_msg_option()
            time.sleep(self.pause)
            self.klik(self.xpath['forward'])
            time.sleep(self.pause)
            self.click_msg_to_fwd(n)
            time.sleep(self.pause)
            self.click_fwd_btn()
            time.sleep(self.pause)
            self.count = 0
            for target in subtarget:
                self.fill_click_target_fwd(target)
            self.klik(self.xpath['send'])
        self.report['sent'] = self.temp

    def check_contacts(self, names: list):
        self.report = pd.DataFrame({'name': names})
        self.temp = []
        for name in names:
            self.looptilactive()
            self.search_name(name)
            try:
                self.cek_n_klik(f'//span[@title="{name}"]', t=3)
                self.temp.append(1)
            except TimeoutException:
                self.temp.append(0)
            finally:
                time.sleep(self.pause)
        self.report['available'] = self.temp

    # Other commands
    def clickable(self, xpath, t=45):
        wait = WebDriverWait(self.__driver, t)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        time.sleep(self.pause)

    def doesexist(self, xpath, t=45):
        wait = WebDriverWait(self.__driver, t)
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        time.sleep(self.pause)

    def looptilactive(self):
        while not self.isactive():
            print('Can\'t continue. Need connection!')
            time.sleep(5)

    def import_contact(self, filename='contact.xlsx'):
        # df = pd.read_excel(f'./contact/{filename}')
        df = pd.read_excel(filename)
        df = df.dropna()
        self.contact = df.iloc[:, :1].values.ravel()

    def export(self, filename='report.xlsx'):
        self.report.to_excel(f'./report/{filename}', index=False)

    def close(self):
        self.__driver.quit()


class BlastData():
    def __init__(self):
        self.contact = None
        self.report = None

    def import_contact(self, filepath):
        df = pd.read_excel(filepath)
        df = df.dropna()
        self.contact = df.iloc[:, :1].values.ravel()


if __name__ == '__main__':
    pass
    # x = '//div[@tabindex="-1"]'
    # elems = t.b.find_elements(t.By.XPATH, x)
    # child = elems[-3].find_element(t.By.TAG_NAME, "div")
    # t.ActionChains(t.b).move_to_element(child).perform()
    # m = '//span[@data-testid="down-context"]/parent::*/parent::*'

