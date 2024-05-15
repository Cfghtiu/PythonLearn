import sys
from PyQt5.QtWidgets import QApplication
from Client import Client


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Client()
    win.show()
    sys.exit(app.exec_())
