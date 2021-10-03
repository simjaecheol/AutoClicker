import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from pynput import mouse, keyboard
from functools import partial

form_class = uic.loadUiType("auto-clicker.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.interval = 0

        self.initialize()
        self.connect_events()
    
    def initialize(self):
        self.spinbox_scroll.setValue(0)
        self.spinbox_scroll.setRange(0, 10000)

        self.table_cmd_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def connect_events(self):
        # commands
        self.button_execution.clicked.connect(self.cmd_execution)

        # auto click
        self.button_run.clicked.connect(self.auto_click)

        # mouse
        self.button_left_click.clicked.connect(partial(self.click, True))
        self.button_right_click.clicked.connect(partial(self.click, False))
        self.button_drag.clicked.connect(self.drag)

        # scroll
        self.button_scroll_up.clicked.connect(partial(self.scroll, False))
        self.button_scroll_down.clicked.connect(partial(self.scroll, True))
        
        # keyboard
        self.button_press_key.clicked.connect(self.press_key)
        self.button_release_key.clicked.connect(self.release_key)
        self.button_release_all.clicked.connect(self.release_all)
        
        # add
        self.spinbox_interval.valueChanged.connect(self.set_interval)
        self.button_add_command.clicked.connect(self.add_cmd)

        # calender
        self.button_1st_day.clicked.connect(self.regist_1st_day)
        self.button_14th_day.clicked.connect(self.regist_14th_day)

        # text
        self.button_add_text.clicked.connect(self.add_text)

    def set_interval(self):
        self.interval = self.spinbox_interval.getValue()

    # connected functions
    def add_cmd(self):
        print(f'add command')

        self.table_cmd_list.setRowCount(10)
        for idx in range(10):
            self.table_cmd_list.setItem(idx, 0, QTableWidgetItem(0))


    def cmd_execution(self):
        print(f'execution')

    def auto_click(self):
        print(f'auto_click')
    
    def click(self, left=True):
        if left:
            print(f'left click')
        else:
            print(f'right click')
    
    def drag(self):
        print(f'from to')
    
    def scroll(self, down=True):
        scrolled_pixel = self.spinbox_scroll.value()
        if down:
            print(f'scroll {scrolled_pixel} down')
        else:
            print(f'scroll {scrolled_pixel} up')

    def press_key(self):
        print(f'press key')

    def release_key(self):
        print(f'release key') 
    
    def release_all(self):
        print(f'release all')

    def regist_1st_day(self):
        print(f'1st day')

    def regist_14th_day(self):
        print(f'14th day')

    def add_text(self):
        print(f'add text')


if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()