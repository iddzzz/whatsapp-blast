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
import threading

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
        ActionChains(self.__driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
            Keys.SHIFT).perform()

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

    def clear_search_field(self):
        search = self.__driver.find_element(By.XPATH, self.xpath['search_name'])
        search.clear()

    def choose_name_or_group(self, name='CHECK'):
        self.klik(f'//span[@title="{name}"]')

    def is_name_exist(self, name):
        self.search_name(name)
        time.sleep(self.pause)
        result = False
        try:
            self.cek_n_klik(f'//span[@title="{name}"]', t=3)
            result = True
        except ElementNotInteractableException:
            print(f"Can't click {name}!")
            result = False
        except TimeoutException:
            print(f"Can't find {name}!")
            result = False
        finally:
            return result

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

    def import_contact(self, filename='./contact/contact.xlsx', name_col=None):
        if name_col is None:
            df = pd.read_excel(filename)
        else:
            df = pd.read_excel(filename, usecols=[name_col])

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

    def send_messages_with_variables(self, excel='./contact/testing-blast-variable.xlsx', txt='message.txt',
                                     col_filter=None):
        """
        Args:
            target
            msgs: list of dictionary
        """
        df = pd.read_excel(excel)
        assert len(df.columns) > 1, 'Number of columns should be > 1'

        df = df[df[col_filter] == 1] if col_filter is not None else df

        with open(txt, "r") as the_file:
            text = the_file.read()

        for i, row in df.iterrows():
            self.looptilactive()
            edited_text = text
            for column in df.columns:
                if column == 'name':
                    continue
                if f'<<{column}>>' in edited_text:
                    edited_text = edited_text.replace(f'<<{column}>>', row[column])
            edited_text = edited_text.split('\n')

            target = row['name']
            if self.is_name_exist(target):
                self.search_name(target)
                time.sleep(self.pause)
                self.choose_name_or_group(target)
                time.sleep(self.pause)
                self.type_message(edited_text)
                self.enter()
            else:
                print(f'{target} does not exist in your contact')

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


import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

qt_creator_file = "wablast.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
tick = QtGui.QColor('green')
white = QtGui.QColor('white')


class ReportModel(QtCore.QAbstractListModel):
    def __init__(self, *args, contact=None, **kwargs):
        super(ReportModel, self).__init__(*args, **kwargs)
        self.contact = contact or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure
            _, text = self.contact[index.row()]
            # Return the doto text only
            return text

        if role == Qt.DecorationRole:
            status, _ = self.contact[index.row()]
            if status:
                return tick
            else:
                return white

    def rowCount(self, index):
        return len(self.contact)


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.contactmodel = ReportModel()
        self.contactView.setModel(self.contactmodel)
        self.dfmodel = DataFrameModel()
        self.tableView.setModel(self.dfmodel)
        self.blast = Blast('root-profile.ini')

        # Connect the button
        self.connectButton.pressed.connect(self.access)
        self.sendButton.pressed.connect(self.send_messages)
        self.setTargetButton.pressed.connect(self.set_target)
        self.forwardButton.pressed.connect(self.forward)
        self.clearTargetButton.pressed.connect(self.clear_target)

        # Connect the menu
        self.actionOpen_Excel.triggered.connect(self.open_excel)

    def open_excel(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Excel', "/home/iddzzz/Files", 'Excel File (*.xlsx)')
        if fname:
            df = pd.read_excel(fname)
            self.dfmodel.setDataFrame(df)
            self.dfmodel.layoutChanged.emit()

    def access(self):
        threading.Thread(target=self.blast.access).start()
        return

    def set_target(self):
        indexes = self.tableView.selectedIndexes()
        if indexes:
            temp = self.dfmodel.dataFrame
            for index in indexes:
                self.contactmodel.contact.append([False, temp.at[index.row(), temp.columns[index.column()]]])
            del temp
            self.contactmodel.layoutChanged.emit()
        else:
            self.statusbar.showMessage("No data selected")

    def clear_target(self):
        self.contactmodel.contact = []
        self.contactmodel.layoutChanged.emit()

    def forward_messages(self, blast_obj, source, n: int, targets=None):
        if targets is None:
            targets = blast_obj.contact
        assert type(targets) == list, "targets should be a list"
        if not len(targets):
            print('targets is empty, cant forward to any contact')
            return
        blast_obj.report = pd.DataFrame({'name': targets})
        blast_obj.temp = []
        all_target = utils.list_partition(targets)
        i = 0
        m = len(targets)
        for subtarget in all_target:
            blast_obj.looptilactive()
            blast_obj.choose_name_or_group(source)
            time.sleep(blast_obj.pause)
            blast_obj.hover_last_message()
            time.sleep(blast_obj.pause)
            blast_obj.click_msg_option()
            time.sleep(blast_obj.pause)
            blast_obj.klik(blast_obj.xpath['forward'])
            time.sleep(blast_obj.pause)
            blast_obj.click_msg_to_fwd(n)
            time.sleep(blast_obj.pause)
            blast_obj.click_fwd_btn()
            time.sleep(blast_obj.pause)
            blast_obj.count = 0
            for target in subtarget:
                i += 1
                blast_obj.fill_click_target_fwd(target)
                self.statusbar.showMessage(f'Forwarding messages... ({i}/{m})')
                self.contactmodel.contact[i - 1][0] = True
                # self.contactmodel.dataChanged.emit(PyQt5.QtCore.QModelIndex, PyQt5.QtCore.QModelIndex)
                self.contactmodel.dataChanged.emit(self.contactmodel.index(i - 1, 0), self.contactmodel.index(i - 1, 0))
            blast_obj.klik(blast_obj.xpath['send'])
        blast_obj.report['sent'] = blast_obj.temp
        self.statusbar.showMessage(f'Forwarding completed ({i}/{m})')

    def forward(self):
        try:
            assert len(self.contactmodel.contact) > 0, "No target found."
            targets = []
            for _, name in self.contactmodel.contact:
                targets.append(name)
            from_whom = self.fromForwardEdit.text()
            total_messages = int(self.numberForwardEdit.text())
            if from_whom and total_messages > 0:
                threading.Thread(target=self.forward_messages,
                                 args=[self.blast, from_whom, total_messages, targets]).start()
                return
        except Exception as why:
            self.statusbar.showMessage(str(why))

    def send_messages(self):
        try:
            text = self.textEdit.toPlainText()
            assert text != '', 'Type a message'
            assert not self.dfmodel.dataFrame.empty and len(self.contactmodel.contact) != 0,\
                'No target found'
            assert self.dfmodel.dataFrame.shape[0] == len(self.contactmodel.contact),\
                'Length of the target list and the table should match.'

            col_filter = self.columnFilterEdit.text().strip()
            if col_filter == '':
                col_filter = None
            threading.Thread(target=self.blast.send_messages_with_variables,
                             args=[self.blast, self.dfmodel.dataFrame, text, col_filter]).start()
            return
        except Exception as why:
            self.statusbar.showMessage(str(why))

    def send_messages_with_variables(self, blast_obj, df, txt='This is a message',
                                     col_filter=None):
        """
        Args:
            target
            msgs: list of dictionary
        """
        assert len(df.columns) > 1, 'Number of columns should be > 1'

        df = df[df[col_filter] == 1] if col_filter is not None else df

        row_in_use = df.index
        target_in_use = []
        for i, item in enumerate(self.contactmodel.contact):
            if i in row_in_use:
                target_in_use.append(item[1])


        text = txt

        for i, row in df.iterrows():
            blast_obj.looptilactive()
            edited_text = text
            for column in df.columns:
                if column == 'name':
                    continue
                if f'<<{column}>>' in edited_text:
                    edited_text = edited_text.replace(f'<<{column}>>', row[column])
            edited_text = edited_text.split('\n')

            target = row['name']
            if blast_obj.is_name_exist(target):
                blast_obj.search_name(target)
                time.sleep(blast_obj.pause)
                blast_obj.choose_name_or_group(target)
                time.sleep(blast_obj.pause)
                blast_obj.type_message(edited_text)
                blast_obj.enter()
            else:
                print(f'{target} does not exist in your contact')



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    window.blast.close()
