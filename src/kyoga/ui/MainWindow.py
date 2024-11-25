# -*- coding: utf-8 -*-
"""."""

import subprocess

from PySide6 import QtCore, QtGui, QtWidgets

WEBP_DIR = 'webp'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.application = kwargs.get('application')

        window_size = QtCore.QSize(960, 540)
        self.resize(window_size)
        self.setMinimumSize(window_size)
        self.setWindowTitle('Kyoga')

        vbox = QtWidgets.QVBoxLayout()

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        self.list_view_model = QtGui.QStandardItemModel()

        list_view = QtWidgets.QListView()
        list_view.setModel(self.list_view_model)
        vbox.addWidget(list_view)

        self.lossless = QtWidgets.QCheckBox()
        self.lossless.setText(self.tr('Lossless'))
        vbox.addWidget(self.lossless)

        select_images = QtWidgets.QPushButton()
        select_images.setText(self.tr('Select images'))
        select_images.clicked.connect(self.on_select_images_clicked)
        vbox.addWidget(select_images)

        self.convert_images = QtWidgets.QPushButton()
        self.convert_images.setText(self.tr('Convert images'))
        self.convert_images.clicked.connect(self.on_convert_images_clicked)
        vbox.addWidget(self.convert_images)

        remove_images = QtWidgets.QPushButton()
        remove_images.setText(self.tr('Remove images'))
        remove_images.clicked.connect(self.on_remove_images_clicked)
        vbox.addWidget(remove_images)

    def on_select_images_clicked(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            self.tr('Select images'),
            QtCore.QDir.homePath(),
            self.tr('Images (*.png *.jpg *.jpeg)'),
        )
        if files:
            for file in files:
                self.list_view_model.appendRow(QtGui.QStandardItem(f'{file}'))

    def on_convert_images_clicked(self):
        self.convert_images.setDisabled(True)
        self.statusBar().showMessage(self.tr('Please wait, converting...'))

        cmd = ['cwebp', '-quiet']

        if self.lossless.checkState() == QtCore.Qt.CheckState.Checked:
            cmd.insert(1, '-lossless')

        images = [
            self.list_view_model.item(index).text()
            for index in range(self.list_view_model.rowCount())
        ]
        if images:
            self.list_view_model.clear()
            for image in images:
                file_info = QtCore.QFileInfo(image)

                output_dir = QtCore.QDir(file_info.dir().path())
                output_dir.mkdir(WEBP_DIR)
                output_dir.cd(WEBP_DIR)

                output = output_dir.filePath(f'{file_info.baseName()}.webp')

                cmd.extend((image, '-o', output))
                try:
                    result = subprocess.run(
                        args=cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                except FileNotFoundError as e:
                    message = QtWidgets.QMessageBox(self)
                    message.setTextFormat(QtCore.Qt.TextFormat.RichText)
                    message.setText(
                        f'{e}<br>'
                        '<a href="https://github.com/natorsc/kyoga">GitHub</a>.'
                    )
                    message.open()
                else:
                    self.list_view_model.appendRow(
                        QtGui.QStandardItem(
                            f'{image} - Return code = {result.returncode}',
                        )
                    )
                    self.statusBar().showMessage(
                        self.tr('Conversion completed.'),
                    )
        else:
            self.statusBar().showMessage(self.tr('No images selected'))
        self.convert_images.setDisabled(False)

    def on_remove_images_clicked(self):
        self.list_view_model.clear()


if __name__ == '__main__':
    pass
