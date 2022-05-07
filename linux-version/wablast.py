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
import os

from config import config


class BlastBasis:
    s = Service("./geckodriver")

    def __init__(self, profile):
        self.__options = Options()
        self.__options.add_argument("-profile")
        self.__options.add_argument(config(profile)['profile_path'])
        self.__driver = webdriver.Firefox(service=Blast.s, options=self.__options)
        self.wait = WebDriverWait(self.__driver, 45)
        self.pause = 0.5
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
            'search_name': '//div[@id="side"]//div[@role="textbox"]',
            'active_sign': '//span[@data-testid="alert-notification"]',
            'footer': '//footer',
            'textbox': '//footer//div[@role="textbox"]',  # textbox message
            'attach': '//div[@title="Attach"]',
            'input_image': '//button[@aria-label="Photos & Videos"]//input',
            'dialog': '//div[@role="dialog"]'
        }

    # basic commands
    def klik(self, xpath):
        self.clickable(xpath)
        self.__driver.find_element(By.XPATH, xpath).click()

    def cek_n_klik(self, xpath, t):
        self.doesexist(xpath, t)
        self.__driver.find_element(By.XPATH, xpath).click()

    def access(self, url='https://web.whatsapp.com/'):
        self.__driver.get(url)

    def hover(self, elem):
        ActionChains(self.__driver).move_to_element(elem).perform()

    def element(self, xpath):
        return self.__driver.find_element(By.XPATH, xpath)

    def elements(self, xpath):
        return self.__driver.find_elements(By.XPATH, xpath)

    def enter(self):
        ActionChains(self.__driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

    def shiftenter(self):
        ActionChains(self.__driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()

    def up(self):
        ActionChains(self.__driver).key_down(Keys.ARROW_UP).key_up(Keys.ARROW_UP).perform()

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

    def hover_last_message(self):
        main_panel = self.element(self.xpath['main'])
        main_panel.click()
        self.up()
        self.hover(main_panel)
        elems = main_panel.find_elements(By.XPATH, self.xpath['messages'])
        child = elems[-1].find_element(By.TAG_NAME, 'div')
        child = child.find_element(By.TAG_NAME, 'div')
        self.hover(child)

    def click_msg_option(self):
        main_panel = self.__driver.find_element(By.XPATH, self.xpath['main'])
        elems = main_panel.find_elements(By.XPATH, self.xpath['messages'])
        self.doesexist(self.xpath['msg_option'], 3)
        elems[-1].find_element(By.XPATH, self.xpath['msg_option']).click()

    def type_message(self, lines: list):
        for line in lines:
            self.element(self.xpath['textbox']).send_keys(line)
            time.sleep(0.2)
            self.shiftenter()

    def attach_image(self, filepath):
        self.element(self.xpath['attach']).click()
        time.sleep(self.pause)
        self.element(self.xpath['input_image']).send_keys(filepath)

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

    def close(self):
        self.__driver.quit()


class Blast(BlastBasis):
    def __init__(self, profile='profile.ini'):
        super().__init__(profile)
        self.contact = ['Father']
        self.report = pd.DataFrame()
        self.count = 0
        self.temp = []
        self.fwd_number = 1

    def import_contact(self, filename='./contact/contact.xlsx'):
        df = pd.read_excel(filename)
        df = df.dropna()
        self.contact = df.iloc[:, :1].values.ravel().tolist()

    def export(self, filename='report.xlsx'):
        self.report.to_excel(f'./report/{filename}', index=False)

    def check_contacts(self, names=None):
        if names is None:
            names = self.contact
        assert type(names) == list, "names should be a list"
        if not len(names):
            print('names is empty, cant check any contact')
            return
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

    def forward(self, source, n: int, targets=None):
        if targets is None:
            targets = self.contact
        assert type(targets) == list, "targets should be a list"
        if not len(targets):
            print('targets is empty, cant forward to any contact')
            return
        self.report = pd.DataFrame({'name': targets})
        self.temp = []
        all_target = utils.list_partition(targets)
        for subtarget in all_target:
            self.looptilactive()
            self.choose_name_or_group(source)
            time.sleep(self.pause)
            self.hover_last_message()
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

    def fill_click_target_fwd(self, name):
        search = self.element(self.xpath['search_fwd'])
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

    # Forward message(s)
    def click_fwd_msg(self):
        self.klik(self.xpath['forward'])

    def click_msg_to_fwd(self, n=1):
        checkboxes = self.elements(self.xpath['checkbox_fwd'])
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

    def send_fwd(self):
        self.klik(self.xpath['send'])

    def send_message(self, target, lines):
        self.search_name(target)
        time.sleep(self.pause)
        self.choose_name_or_group(target)
        time.sleep(self.pause)
        self.type_message(lines)
        self.enter()

    def send_messages(self, target, msgs):
        """
        Args:
            target
            msgs: list of dictionary
        """
        self.search_name(target)
        time.sleep(self.pause)
        self.choose_name_or_group(target)
        time.sleep(self.pause)
        for msg in msgs:
            if msg['type'] == 'lines' or msg['type'] == 'txt':
                self.type_message(msg['content'])
                self.enter()
            elif msg['type'] == 'pic':
                self.attach_image(msg['content'])
                time.sleep(2)
                self.enter()

    def message_to_number(self, phone):
        # FIXME: when the url valid or invalid
        self.access(f'https://web.whatsapp.com/send?phone={phone}&text&app_absent=0')
        invalid_msg = 'Phone number shared via url is invalid.'
        self.doesexist(self.xpath['dialog'], t=45)
        time.sleep(2)
        try:
            if invalid_msg in self.element(self.xpath['dialog']).text:
                print('Phone not found')
                self.element('//div[@role="button"]').click()
                return
            else:
                return
        except NoSuchElementException:
            print('Go go go')


if __name__ == '__main__':
    b = Blast('root-profile.ini')
    try:
        b.access()
        b.looptilactive()
        b.send_messages('CHECK', [utils.lines(['Check', '456']), utils.picture('picture.png'), utils.txt('message.txt')])
        time.sleep(20)
    except Exception:
        print('Error')
    finally:
        b.close()
