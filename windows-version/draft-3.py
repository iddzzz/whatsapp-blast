import tkinter as tk
from tkinter.filedialog import askopenfilename
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
from selenium.webdriver.chrome.service import Service
import pandas as pd


class Blast(tk.Frame):

    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Saidzzz\AppData\Local\Google\Chrome\User Data\Default')
    options.add_argument('--profile-directory=Default')
    s = Service('./chromedriver/chromedriver.exe')

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.parent.title("WhatsApp Blast")
        self.parent.rowconfigure(0, minsize=500, weight=1)
        self.parent.columnconfigure(1, minsize=500, weight=1)
        self.parent.columnconfigure(2, minsize=250, weight=1)

        # Frames
        self.fr_buttons = tk.Frame(self, relief=tk.RAISED)
        self.fr_target = tk.Frame(self, relief=tk.RIDGE)
        self.fr_action = tk.Frame(self, relief=tk.RAISED)

        # Buttons on fr_buttons
        self.btn_connect = tk.Button(self.fr_buttons, text="Connect", command=self.access)
        self.btn_import = tk.Button(self.fr_buttons, text="Import Contact", command=self.impor_kontak)
        self.btn_close_browser = tk.Button(self.fr_buttons, text="Safely Close", command=self.close)
        self.btn_connect.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_import.grid(row=1, column=0, sticky="ew", padx=5)
        self.btn_close_browser.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Elements on fr_target
        self.lbl_target = tk.Label(self.fr_target, text="Test", anchor="w")
        self.lbl_target.pack()

        # Attach frames
        self.fr_buttons.grid(row=0, column=0, sticky="ns")
        self.fr_target.grid(row=0, column=1, sticky="nsew")
        self.fr_action.grid(row=0, column=2, sticky="nsew")

        self.driver = webdriver.Chrome(service=Blast.s, options=Blast.options)
        self.wait = WebDriverWait(self.driver, 45)
        self.active = False
        self.fwd_number = 1
        self.pause = 0.5
        self.contact = ['Father']
        self.temp = []
        self.report = pd.DataFrame()
        self.xpath = {
            'messages': '//div[@class="Nm1g1 _22AX6"]',
            'msg_option': '//span[@data-testid="down-context"]',
            'forward': '//div[@aria-label="Forward message"]',
            'fwd_btn': '//button[@title="Forward message"]',
            'fwds_btn': '//button[@title="Forward messages"]',
            'search_fwd': '//div[@role="textbox"]',
            'send': '//div[@role="button"]',
            'checkbox_fwd': '//div[@data-testid="visual-checkbox"]',
            'search_name': '//div[@title="Search input textbox"]',
            'active_sign': '//span[@data-testid="alert-notification"]'
        }

        # <create the rest of your GUI here>

    # Common commands
    def klik(self, xpath):
        self.clickable(xpath)
        self.driver.find_element(By.XPATH, xpath).click()

    def cek_n_klik(self, xpath, t):
        self.doesexist(xpath, t)
        self.driver.find_element(By.XPATH, xpath).click()

    def access(self, url='https://web.whatsapp.com/'):
        self.driver.get(url)

    # Specific commands
    def isactive(self):
        try:
            self.doesexist(self.xpath['active_sign'], t=3)
            return True
        except TimeoutException:
            return False

    def search_name(self, name='Mother'):
        search = self.driver.find_element(By.XPATH, self.xpath['search_name'])
        search.clear()
        search.send_keys(name)

    def choose_name_or_group(self, name='CHECK'):
        self.klik(f'//span[@title="{name}"]')

    def click_msg_option(self):
        elems = self.driver.find_elements(By.XPATH, self.xpath['messages'])
        ActionChains(self.driver).move_to_element(elems[-1]).perform()  # hover over
        self.klik(self.xpath['msg_option'])

    # Forward message(s)
    def click_fwd_msg(self):
        self.klik(self.xpath['forward'])

    def click_msg_to_fwd(self, n=1):
        checkboxes = self.driver.find_elements(By.XPATH, self.xpath['checkbox_fwd'])
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
        search = self.driver.find_element(By.XPATH, self.xpath['search_fwd'])
        search.send_keys(name)
        time.sleep(self.pause)
        try:
            self.cek_n_klik(f'//span[@title="{name}"]', t=3)
            self.temp.append(1)
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
        wait = WebDriverWait(self.driver, t)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        time.sleep(self.pause)

    def doesexist(self, xpath, t=45):
        wait = WebDriverWait(self.driver, t)
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

    def impor_kontak(self):
        filepath = askopenfilename(
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        self.import_contact(filepath)
        self.lbl_target["text"] = self.contact

    def export(self, filename='report.xlsx'):
        self.report.to_excel(f'./report/{filename}', index=False)

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    b = Blast(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
