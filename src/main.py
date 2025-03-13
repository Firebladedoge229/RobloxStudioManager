import sys
class FilteredStdout:
    def __init__(self, stream, text_to_filter):
        self.stream = stream
        self.text_to_filter = text_to_filter

    def write(self, message):
        if self.text_to_filter not in message:
            self.stream.write(message)

    def flush(self):
        self.stream.flush()

sys.stdout = FilteredStdout(sys.stdout, "QFluentWidgets")
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
    setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    main_window = Window()
    main_window.show()
    app.exec_()
