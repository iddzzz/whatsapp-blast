from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import contact


# membaca pesan txt ke string
import utils


def message(path="messages.txt"):
    with open(path, "r") as pesan:
        messages = pesan.read()
    return messages


# klik kirim
def kirim(driver):
    time.sleep(1)
    button = driver.find_element_by_xpath('//button[@class="_1E0Oz"]')
    time.sleep(1)
    button.click()
    time.sleep(2)


# masuk whatsapp
def masuk(url="https://web.whatsapp.com/"):
    # Option for loading previous data on Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\Saidzzz\AppData\Local\Google\Chrome\User Data\Default')
    options.add_argument('--profile-directory=Default')

    driver = webdriver.Chrome(executable_path=r"D:/physics/machine-learning/chromedriver.exe", options=options)
    driver.get(url)
    # time.sleep(45)
    WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/span/div/div/div[2]/div[1]')))
    return driver


def tulis(driver, string, delay=1):
    try:
        # driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]').click()
        time.sleep(2)
        for line in string.splitlines():
            ActionChains(driver).send_keys(line).perform()
            ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(
                Keys.ENTER).perform()
        time.sleep(delay)
        ActionChains(driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
    except NoSuchElementException as se:
        print("Whatt!!!", se)
        time.sleep(2)
    except Exception as e:
        print(e)
        time.sleep(2)


def cari(driver, nama):
    search = driver.find_element_by_xpath('//div[@class="_13NKt copyable-text selectable-text"]')
    time.sleep(2)
    a = ActionChains(driver)
    a.move_to_element(search).click().perform()
    search.send_keys(nama)
    try:
        # time.sleep(3)
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//span[@title="{}"]'.format(nama))))

        user = driver.find_element_by_xpath('//span[@title="{}"]'.format(nama))
        user.click()
        time.sleep(1)
        search.clear()
        return True
    except NoSuchElementException as se:
        print(se, nama, "doesn't exist")
        search.clear()
        time.sleep(1)
        return False
    except Exception as e:
        print(e, 'Error?')
        # checklist.append('idk it is failed')
        search.clear()
        time.sleep(1)
        return False


def cari_untuk_forward(driver, the_name, delay=1, the_xpath='//div[@class="_2_1wd copyable-text selectable-text"]'):
    # Search nama
    search = driver.find_element_by_xpath(the_xpath)
    search.send_keys(the_name)

    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//span[@title="{}"]'.format(the_name))))
        # Klik nama
        driver.find_element_by_xpath('//span[@title="{}"]'.format(the_name)).click()
        time.sleep(delay)
        search.clear()
    except Exception as why:
        print(why, '{} does not exist (maybe)'.format(the_name))
        search.clear()
        time.sleep(1)


def attach(browser, file_path):
    attachment_section = browser.find_element_by_xpath('//div[@title = "Attach"]')
    attachment_section.click()
    image_box = browser.find_element_by_xpath('//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
    image_box.send_keys(file_path)
    time.sleep(3)
    # send_button = browser.find_element_by_xpath('//span[@data-icon="send-light"]')
    # send_button.click()
    ActionChains(browser).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
    time.sleep(2)


# loading contact, pandas to list
def loading_contact(csv_path, nama_kolom='Name'):
    df = pd.read_csv(csv_path)
    return list(df[nama_kolom].values)


# menunggu whatsapp terhubung
def tunggu_connected(driver):
    WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/span/div/div/div[2]/div[1]')))
    while True:
        try:
            if driver.find_element_by_xpath(
                    '//*[@id="side"]/span/div/div/div[2]/div[1]').text == "Computer not connected":
                time.sleep(2)
                continue
            elif driver.find_element_by_xpath(
                    '//*[@id="side"]/span/div/div/div[2]/div[1]').text == "Phone not connected":
                time.sleep(2)
                continue
            elif driver.find_element_by_xpath(
                    '//*[@id="side"]/span/div/div/div[2]/div[1]').text == "Connecting":
                time.sleep(2)
                continue
            else:
                break
        except Exception as why:
            print(why, "Not connected")
            time.sleep(5)
            continue
    # print("Connected")


# Forward 1 last pesan dari nama ke 5 nama | (string, list of string (max 5))
def forward(driver, the_from, the_to):
    try:
        # Dipastikan ada
        check = cari(driver, the_from)
        if not check:
            print("Nothing")

        # Making an instance/object of action
        a = ActionChains(driver)
        # Making an instance/object of driver wait
        wait = WebDriverWait(driver, 45)

        # Letak pesan
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="_1bR5a"]')))
        time.sleep(1)
        m = driver.find_elements_by_xpath('//div[@class="_1bR5a"]')

        # Hover pesan terakhir
        a.move_to_element(m[-1]).perform()

        # Ke menu2 tempat tombol forward
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="_39Lm1 _3qSKL"]')))
        driver.find_element_by_xpath('//div[@class="_39Lm1 _3qSKL"]').click()

        # Klik forward message
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Forward message"]')))
        time.sleep(1)
        driver.find_element_by_xpath('//div[@aria-label="Forward message"]').click()

        # Forward to
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[@title="Forward message"]')))
        time.sleep(1)
        driver.find_element_by_xpath('//button[@title="Forward message"]').click()

        # target max 5
        for tujuan in the_to:
            cari_untuk_forward(driver, tujuan)
            time.sleep(1)

        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="button"]')))

        while True:
            try:
                # Kirim
                driver.find_element_by_xpath('//div[@role="button"]').click()
                break
            except Exception as what_happen:
                print(what_happen)
                time.sleep(1)
    except Exception as why:
        print(why, "Whatt??")


# blasting-info
def blasting(chrome):
    # target = ['CHECK', 'Moth', 'Father']
    target, wilayah, link, _, _ = contact.generating_custom(kolom_1='WIL', kolom_2='LINK')

    for i, tujuan in enumerate(target):
        tunggu_connected(chrome)
        print(i+1, '/', len(target))
        try:
            check = cari(chrome, tujuan)
            if check == False:
                continue
            # tulis(chrome, message())
            # kirim(chrome)
            # attach(chrome, r"D:\khuddam\kpa\Kisi-Kisi Seleksi LCT Khilafat 2021.pdf")

            pesan = message()
            pesan = pesan.replace('<<wilayah>>', str(wilayah[i]))
            pesan = pesan.replace('<<link>>', str(link[i]))

            tulis(chrome, pesan)
            # kirim(chrome)
            tulis(chrome, utils.ganti_sapaan(str(tujuan), message("messages-2.txt")))
            # tulis(chrome, message("messages-3.txt"))
            # kirim(chrome)
        except Exception as what_happen:
            print(what_happen)
            continue

    while True:
        time.sleep(5)
    # chrome.close()
    # sys.exit()


# blasting untuk tanya rekening
def blasting_rekening():
    target, the_cng, the_rekenings, rek_usernames, the_banks = contact.generating_for_blast_rekening()

    chrome = masuk()

    for i, tujuan in enumerate(target):
        tunggu_connected(chrome)
        print(i + 1, '/', len(target))
        try:
            check = cari(chrome, tujuan)
            if check == False:
                continue

            pesan = message()
            pesan = pesan.replace('<<cng>>', str(the_cng[i]))
            pesan = pesan.replace('<<nomor rekening>>', str(the_rekenings[i]))
            pesan = pesan.replace('<<nama rekening>>', str(rek_usernames[i]))
            pesan = pesan.replace('<<nama bank>>', str(the_banks[i]))

            
            tulis(chrome, pesan)
            
        except Exception as what_happen:
            print(what_happen)
            continue

    time.sleep(5)
    # chrome.close()
    # sys.exit()


# Blasting dana terkirim
def blasting_dana_sent():
    target, the_cng, the_nominals, rek_usernames, the_banks = contact.generating_for_blast_rekening_terkirim()

    chrome = masuk()

    for i, tujuan in enumerate(target):
        tunggu_connected(chrome)
        print(i + 1, '/', len(target))
        try:
            check = cari(chrome, tujuan)
            if check == False:
                continue

            pesan = message()
            pesan = pesan.replace('<<cng>>', str(the_cng[i]))
            pesan = pesan.replace('<<nominal>>', str(the_nominals[i]))
            pesan = pesan.replace('<<nama rekening>>', str(rek_usernames[i]))
            pesan = pesan.replace('<<nama bank>>', str(the_banks[i]))

            
            tulis(chrome, pesan)
            
        except Exception as what_happen:
            print(what_happen)
            continue

    while True:
        time.sleep(5)
    # chrome.close()
    # sys.exit()


if __name__ == '__main__':

    # targets = ['CHECK', 'Moth', 'Whatt', 'Uwu', 'Ehem', 'Abid']
    # targets = contact.generating_for_blast()

    chrome = masuk()
    blasting(chrome)
    # tunggu_connected(chrome)

    # targets = utils.list_partition(targets)

    # for lima_kontak in targets:
    #    tunggu_connected(chrome)
    #    forward(chrome, 'CHECK', lima_kontak)
    #    time.sleep(3)


