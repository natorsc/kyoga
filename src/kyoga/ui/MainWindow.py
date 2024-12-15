# -*- coding: utf-8 -*-
"""."""

import functools

from PySide6 import QtCore, QtGui, QtWidgets

WEBP_DIR = 'webp'


class MainWindow(QtWidgets.QMainWindow):
    counter = 0

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
        self.list_view_model.clear()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            self.tr('Select images'),
            QtCore.QDir.homePath(),
            self.tr('Images (*.png *.jpg *.jpeg)'),
        )
        if files:
            for file in files:
                self.list_view_model.appendRow(QtGui.QStandardItem(f'{file}'))

    def on_process_finished(
        self, exit_code, exit_status, image, process, total
    ):
        if exit_code != 0:
            # Create log.
            print(process.readAllStandardOutput().data().decode())
            print(process.readAllStandardError().data().decode())
        else:
            self.list_view_model.appendRow(
                QtGui.QStandardItem(
                    f'{image} - Return code = {exit_code}',
                )
            )
        process.deleteLater()
        self.counter += 1
        message = self.tr(f'{self.counter} of {total}.')
        self.statusBar().showMessage(message)
        if self.counter == total:
            self.statusBar().showMessage(message + self.tr(' Complete'))
            self.counter = 0

    def on_error_occurred(self, process_error):
        if process_error.name == 'FailedToStart':
            message = QtWidgets.QMessageBox(self)
            message.setTextFormat(QtCore.Qt.TextFormat.RichText)
            message.setText(
                'cwebp is not installed.<br>'
                '<a href="https://github.com/natorsc/kyoga">GitHub</a>.'
            )
            message.open()

    def on_convert_images_clicked(self):
        self.convert_images.setDisabled(True)
        self.statusBar().showMessage(
            self.tr('Please wait, converting...'),
            2000,
        )

        cmd = 'cwebp -quiet'
        if self.lossless.checkState() == QtCore.Qt.CheckState.Checked:
            cmd += ' -lossless'

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

                process = QtCore.QProcess()
                process.finished.connect(
                    functools.partial(
                        self.on_process_finished,
                        image=image,
                        process=process,
                        total=len(images),
                    )
                )
                process.errorOccurred.connect(self.on_error_occurred)

                if process.state() == QtCore.QProcess.NotRunning:
                    cmd += f' "{image}" -o "{output}"'
                    process.startCommand(cmd)

        else:
            self.statusBar().showMessage(self.tr('No images selected'))
        self.convert_images.setDisabled(False)

    def on_remove_images_clicked(self):
        self.list_view_model.clear()


if __name__ == '__main__':
    print('[!] run app.py [!]')
