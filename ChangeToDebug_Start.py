from PyQt5 import QtWidgets

from ChangeToDebug_Controller import *

if __name__ == '__main__':
    import sys

    args = argparse_function(Version)
    app = QtWidgets.QApplication(sys.argv)
    window = myMainWindow()
    window.show()
    sys.exit(app.exec_())