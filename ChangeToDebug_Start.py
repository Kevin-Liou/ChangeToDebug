"""ChangeToDebug 進入點。

實作已整合至 changetodebug 套件：
    changetodebug/core   修補引擎、profile 載入、各功能 task
    changetodebug/gui    PyQt5 介面
"""

import sys

from changetodebug.app import main

if __name__ == "__main__":
    sys.exit(main())
