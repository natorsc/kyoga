# -*- coding: utf-8 -*-
"""."""

import sys

from PySide6 import QtCore, QtGui, QtWidgets

from kyoga import resources_rc
from kyoga.ui.MainWindow import MainWindow

RESOURCES_RC = resources_rc


def main():
    APP_NAME = 'kyoga'

    application = QtWidgets.QApplication(sys.argv)
    application.setOrganizationName(APP_NAME)
    application.setOrganizationDomain(APP_NAME)
    application.setApplicationName(APP_NAME)
    application.setDesktopFileName(APP_NAME)
    application.setWindowIcon(QtGui.QIcon(':/icons/kyoga'))

    loc = QtCore.QLocale.system()
    translator = QtCore.QTranslator(application)
    if translator.load(QtCore.QLocale(loc), APP_NAME, '.', ':/locales'):
        application.installTranslator(translator)

    if QtCore.QSysInfo.productType() == 'windows':
        from ctypes import windll

        windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_NAME)

    window = MainWindow(application=application)
    window.show()

    sys.exit(application.exec())


if __name__ == '__main__':
    main()
