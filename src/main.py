import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from coordinator import Coordinator
from ui.main_window import MainWindow

def main():
    # Set AppUserModelID for Windows to show the correct taskbar icon
    if os.name == 'nt':
        myappid = 'geiminicli.autoclicker.flow.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    
    # Initialize Coordinator
    coordinator = Coordinator()
    
    # Initialize and show the MainWindow
    window = MainWindow(coordinator)
    window.show()
    
    print("AutoClicker Started.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
