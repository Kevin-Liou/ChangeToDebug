"""
Created on 2020/11/25

author:
- Kevin Liou

Summary:
This program is a PyQt5-based graphical user interface (GUI) tool designed to automatically modify debug settings in Intel G9 and G9R codebases. The tool allows the user to select either "Memory Debug" or "Single Driver Debug" modes, enter the desired file names, and apply the modifications to the specified files.

Features:
- Enables PcdHpMemoryDebugEnable setting in PlatformPcdConfig.dsc
- Replaces IsLegacySupported() with 0 in DxeMemDebugAcpiArea.c
- Finds and modifies .c files in specified folders to change DEBUG_WARN and DEBUG_INFO messages to DEBUG_ERROR
- For "Memory Debug" mode, modifies related .inf files to include memory debug settings

Returns:
None. The program makes modifications directly to the specified files in the user's file system.
"""

import os, logging, argparse, Ui_ChangeToDebug_main, Ui_ChangeToDebug_log, Ui_ChangeToDebug_about

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

Version = "1.0.0"

current_path = os.getcwd()
file_name = "PlatformPcdConfig.dsc"
directory = "\HpPlatformPkg\MultiProject"
old_string = "PcdHpMemoryDebugEnable              |FALSE"
new_string = "PcdHpMemoryDebugEnable              |TRUE"

file_name2 = "DxeMemDebugAcpiArea.c"
directory2 = "\HpPe\HpCommonPkg\MemoryDebug\Dxe\DxeMemDebugAcpiArea\\"
old_string2 = "IsLegacySupported()"

need_process_folder = ["\HpPlatformPkg", "\HpPe", "\Edk2", "\Edk2Platforms", "\HpCore", "\HpEpsc", "\HpIntel", "\Intel"]

def argparse_function(ver):
    parser = argparse.ArgumentParser(prog='ReleasePkg.py', description='Tutorial')
    parser.add_argument("-d", "--debug", help='Show debug message.', action="store_true")
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()
    if args.debug:
        Debug_Format = "%(levelname)s, %(funcName)s: %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=Debug_Format)  #Debug use flag
        print("Enable debug mode.")
    return ver

# Enable PcdHpMemoryDebugEnable
def EnablePcdHpMemoryDebugEnable(print_func):
    if os.path.exists(current_path + directory):
        for root, dirs, files in os.walk(current_path + directory):
            for file in files:
                if file == file_name:
                    file_path = os.path.join(root, file)
                    # Open the file and read its contents
                    with open(file_path, "r") as f:
                        file_contents = f.read()
                    # Replace the old string with the new string
                    new_contents = file_contents.replace(old_string, new_string)
                    # Write the modified contents back to the file
                    with open(file_path, "w") as f:
                        f.write(new_contents)
        print_func("Enable PcdHpMemoryDebugEnable Success")

# Replace IsLegacySupported() to 0
def ReplaceIsLegacySupported(print_func):
    if os.path.isfile(current_path + directory2 + file_name2):
        file_path = current_path + directory2 + file_name2
        # Open the file and read its contents
        with open(file_path, "r") as f:
            file_contents = f.read()
        # Replace the old string with the new string
        new_contents = file_contents.replace(old_string2, "0")
        # Write the modified contents back to the file
        with open(file_path, "w") as f:
            f.write(new_contents)
        print_func("Replace IsLegacySupported() to 0 Success")

# Search C file path and search inf file
def Find_C_file(print_func, input_text, debug_mode):
    path = current_path
    inf_file_path = ""
    for text in input_text:
        found_flag = False
        for folder in need_process_folder:
            path = current_path + folder
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".c") and file == text:
                        print_func("Find file: " + os.path.join(root, file))
                        found_flag = True
                        if debug_mode == "memory":
                            Modify_C_file(print_func, os.path.join(root, file))
                            inf_file_path = find_inf_file_with_content(print_func, root, '.inf', text)
                            if os.path.exists(inf_file_path):
                                modify_inf_file(print_func, inf_file_path)
                        if debug_mode == "single driver":
                            Modify_C_file(print_func, os.path.join(root, file))
                            inf_file_path = find_inf_file_with_content(print_func, root, '.inf', text)
                        continue
        if not found_flag:
            print_func(text + " Not found")

# Modify C file to DEBUG_ERROR
def Modify_C_file(print_func, file_path):
    with open(file_path, "r") as f:
        file_content = f.read()
    file_content = file_content.replace("DEBUG_WARN", "DEBUG_ERROR").replace("DEBUG_INFO", "DEBUG_ERROR")
    with open(file_path, "w") as f:
        f.write(file_content)
    print_func("Modify file DEBUG message to DEBUG_ERROR Success")

# Search inf file and modify memory debug mode
def find_inf_file_with_content(print_func, search_path, file_extension, content): # path, .inf, xxxxx.c
    found_flag = False
    if "_" in content:
        content = content.split("_")[0]
    for root, dirs, files in os.walk(search_path, topdown=False):
        for name in files:
            if name.endswith(file_extension):
                file_path = os.path.join(root, name)
                # Load the file content
                with open(file_path, 'r') as f:
                    file_content = f.read()
                    if content in file_content:
                        print_func("Find inf file: " + file_path)
                        found_flag = True
                        return file_path
    if not found_flag:
        print_func("inf file is not found")

# Modify inf file to add memory debug string
def modify_inf_file(print_func, file_path):
    # Determine if the required string already exists
    packages_str = 'HpCommonPkg/MemoryDebug/MemoryDebug.dec'
    libclasses_str = 'MemDebugLib'
    with open(file_path, 'r') as f:
        content = f.readlines()
        found_packages = False
        found_libclasses = False
        for line in content:
            if line.strip() == packages_str:
                found_packages = True
            elif line.strip() == libclasses_str:
                found_libclasses = True
    # If the required string already exists, it will not be modified
    if found_packages or found_libclasses:
        print_func("inf file already modified to debug mode")
        return
    # Read file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # Modify [Packages]
    for i, line in enumerate(lines):
        if line.strip() == "[Packages]":
            # Find the indent in the line under [Packages]
            indent = get_indentation(lines[i+1])
            lines.insert(i+1, indent + "HpCommonPkg/MemoryDebug/MemoryDebug.dec\n")
            break
    # Modify [LibraryClasses]
    for i, line in enumerate(lines):
        if lines[i].strip() == "[LibraryClasses]":
            # Find the indent in the line under [LibraryClasses]
            indent = get_indentation(lines[i+1])
            i += 1
            while i < len(lines):
                if lines[i] != "\n":
                    i += 1
                else:
                    break
            lines.insert(i, indent + "MemDebugLib\n")
            break
    # Write file
    with open(file_path, 'w') as f:
        f.writelines(lines)
    print_func("Modify inf file Success")

# get indentation and return it
def get_indentation(line):
    # Returns the space before the string
    i = 0
    while i < len(line) and line[i] == ' ':
        i += 1
    return line[:i]

class Dialog(QtWidgets.QDialog, Ui_ChangeToDebug_log.Ui_Log):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setupUi(self)
        self.setup_control()

    def setup_control(self):
        self.pushButton.clicked.connect(self.on_end_button_clicked)

    def append_message(self, message):
        if "Success" in message:
            parts = message.split("Success")
            message = f'{parts[0]}<span style="color:green">Success</span>{"".join(parts[1:])}'
        self.textEdit.insertHtml(message + '<br>')

    def on_end_button_clicked(self):
        QtWidgets.QApplication.quit()

class AboutDialog(QtWidgets.QDialog, Ui_ChangeToDebug_about.Ui_About):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

class myMainWindow(QtWidgets.QMainWindow, Ui_ChangeToDebug_main.Ui_MainWindow):
    def __init__(self, parent=None):
        super(myMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setup_control()
        self.message_dialog = Dialog(self)

    def setup_control(self):
        self.pushButton.clicked.connect(self.buttonClicked)
        self.actionAbout.triggered.connect(self.open_about_dialog)

    def print_and_log(self, message):
        print(message)
        self.message_dialog.append_message(message)

    def buttonClicked(self):
        self.message_dialog.show()

        input_text = self.plainTextEdit.toPlainText()
        input_text = input_text.splitlines()
        debug_mode = ""
        if not os.path.exists(current_path + "\HpPlatformPkg"):
            self.print_and_log("Please put this tool into the code...")
            return
        if self.radioButton.isChecked() and len(input_text) != 0:
            self.print_and_log("Start to change to memory debug mode...")
            debug_mode = "memory"
            EnablePcdHpMemoryDebugEnable(self.print_and_log)
            ReplaceIsLegacySupported(self.print_and_log)
            Find_C_file(self.print_and_log, input_text, debug_mode)
        elif self.radioButton_2.isChecked() and len(input_text) != 0:
            self.print_and_log("Start to change to single driver debug mode...")
            debug_mode = "single driver"
            Find_C_file(self.print_and_log, input_text, debug_mode)
        elif len(input_text) == 0:
            self.print_and_log("You didn't enter anything...")
        else:
            self.print_and_log("WTF...")

    def open_about_dialog(self):
        self.about_dialog = AboutDialog(self)
        self.about_dialog.show()

#  Delete the following after development
# if __name__ == '__main__':
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     window = myMainWindow()
#     window.show()
#     sys.exit(app.exec_())