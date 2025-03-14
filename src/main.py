import sys
import colorama
colorama.just_fix_windows_console()
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme
from ui_components import Window

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    setTheme(Theme.AUTO)

    app = QApplication(sys.argv)
    main_window = Window()
    main_window.show()
    app.exec_()