import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from pynput import mouse, keyboard
from functools import partial
from enum import Enum
from threading import Thread
from virtual_mouse import VirtualMouse

form_class = uic.loadUiType("auto-clicker.ui")[0]

stop = False

def auto_click(interval):
    v_mouse = VirtualMouse()
    global stop
    while not stop:
        time.sleep(interval)
        v_mouse.click()

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        return x, y

class Input(Enum):
    NULL = 0
    MOUSE_LEFT_CLICK = 1
    MOUSE_RIGHT_CLICK = 2
    MOUSE_DRAG = 3
    SCROLL_DOWN = 4
    SCROLL_UP = 5
    KEYBOARD_INPUT = 6
    CALENDER_CLICK = 7
    TEXT_INPUT = 8

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.interval = 0
        self.cmd_type = Input.NULL
        self.mouse_ctrl = mouse.Controller
        self.keyboard_ctrl = keyboard.Controller
        self.auto_click_th = None
        
        self.mouse_click_pos = {}
        self.mouse_drag_from = {}
        self.mouse_drag_to = {}

        self.key_list = []
        self.text = ""
        self.cmd_list = []

        self.initialize()
        self.connect_events()
    
    def initialize(self):
        self.spinbox_scroll.setValue(0)
        self.spinbox_scroll.setRange(0, 10000)
        self.spinbox_month.setRange(0, 12)
        self.spinbox_day.setRange(0, 365)
        self.edit_click_interval.setValue(1.0)

        self.edit_execution_time.setTime(QTime.currentTime())
        self.edit_execution_date.setDate(QDate.currentDate())
        self.table_cmd_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def connect_events(self):
        # commands
        self.button_execution.clicked.connect(self.cmd_execution)

        # auto click
        self.button_auto_start.clicked.connect(self.auto_click_start)
        self.button_auto_stop.clicked.connect(self.auto_click_stop)

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
        self.button_calendar_add.clicked.connect(self.calendar_click)

        # text
        self.button_add_text.clicked.connect(self.add_text)

    def set_interval(self):
        self.interval = self.spinbox_interval.getValue()

    # connected functions
    def add_cmd(self):
        print(f'add command')

        self.table_cmd_list.setRowCount(10)
        for idx in range(10):
            self.table_cmd_list.setItem(idx, 0, QTableWidgetItem('0'))
            self.table_cmd_list.setItem(idx, 1, QTableWidgetItem('Click'))
        
        self.cmd_type = Input.NULL


    def cmd_execution(self):
        time = self.edit_execution_time.time()
        date = self.edit_execution_date.date()
        print(f'execution {date} - {time}')

        self.cmd_type = Input.NULL

    def auto_click_start(self):
        interval = self.edit_click_interval.value()
        if self.auto_click_th is None:
            self.auto_click_th = Thread(target=auto_click, args=(interval,))
            global stop
            stop = False
            self.auto_click_th.start()
            print(f'auto click start')
        else:
            print(f'auto click is running')
    
    def auto_click_stop(self):
        if self.auto_click_th is not None:
            global stop
            stop = True
            try:
                self.auto_click_th.join()
            except Exception as e:
                print(f'{e}')
            self.auto_click_th = None
            print(f'auto click stop')
               
    def click(self, left=True):
        with mouse.Listener(on_click=on_click) as listener:
            try:
                listener.join()
            except Exception as e:
                print(f'{e}')
        
        if left:
            self.cmd_type = Input.MOUSE_LEFT_CLICK
            print(f'left click')
        else:
            self.cmd_type = Input.MOUSE_RIGHT_CLICK
            print(f'right click')
    
    def drag(self):
        self.cmd_type = Input.MOUSE_DRAG
        with mouse.Events() as events:
            event = events.get()
        print(event)
        print(f'from to')
    
    def scroll(self, down=True):
        scrolled_pixel = self.spinbox_scroll.value()
        if down:
            self.cmd_type = Input.SCROLL_DOWN
            print(f'scroll {scrolled_pixel} down')
        else:
            self.cmd_type = Input.SCROLL_UP
            print(f'scroll {scrolled_pixel} up')

    def press_key(self):
        self.cmd_type = Input.KEYBOARD_INPUT
        with keyboard.Events() as events:
            event = events.get()
        print(f'press key {event}')

    def release_key(self):
        self.cmd_type = Input.KEYBOARD_INPUT
        with keyboard.Events() as events:
            event = events.get()
        print(f'release key {event}') 
    
    def release_all(self):
        self.cmd_type = Input.KEYBOARD_INPUT
        print(f'release all')

    def regist_1st_day(self):
        print(f'1st day')

    def regist_14th_day(self):
        print(f'14th day')

    def add_text(self):
        self.text = self.input_text.text()
        self.input_text.setText("")
        print(f'add {self.text}')
    
    def calendar_click(self):
        month = self.spinbox_month.value()
        day = self.spinbox_day.value()

        print(f'calendar click {month} / {day}')


if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()