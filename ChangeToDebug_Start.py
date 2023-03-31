from PyQt5 import QtWidgets

from ChangeToDebug_Controller import myMainWindow

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = myMainWindow()
    window.show()
    sys.exit(app.exec_())