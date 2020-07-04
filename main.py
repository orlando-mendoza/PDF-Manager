import sys
import os
import re

from os import path
from PyPDF2 import PdfFileMerger
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QLabel,
                               QMainWindow, QPushButton, QWidget, QTabWidget,
                               QAction, QFileDialog, QLineEdit, QListWidget,
                               QAbstractItemView, QMessageBox, QStatusBar)


class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        # self.setStyleSheet('font-size: 25px;')
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            return super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            return super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            pdf_files = []

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if url.toString().endswith('.pdf'):
                        pdf_files.append(str(url.toLocalFile()))
            self.addItems(pdf_files)
        else:
            return super().dropEvent(event)


class OutputField(QLineEdit):
    def __init__(self):
        super().__init__()
        # self.height = 55
        # self.setStyleSheet('font-size: 30px;')
        # self.setFixedHeight(self.height)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            if event.mimeData().urls():
                self.setText(event.mimeData().urls()[0].toLocalFile())
        else:
            event.ignore()
# class outputField


class Button(QPushButton):
    def __init__(self, label_text):
        super().__init__()
        self.setText(label_text)
        self.setStyleSheet('''
            width: 180px;
        ''')


class TabSinglePDFWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.output_folder_layout = QHBoxLayout()
        self.buttons_layout = QHBoxLayout()

        # Creates and adds the QLineEdit output_file
        self.output_file = OutputField()
        self.output_folder_layout.addWidget(self.output_file)

        # Creates and adds a QPushButton to browse the output file
        self.btn_browse = Button('&Save to')
        self.btn_browse.clicked.connect(self.populate_file_name)
        self.output_folder_layout.addWidget(self.btn_browse)

        # Creates the ListBox Widget
        self.pdf_list_widget = ListWidget()

        # Create the buttons
        self.btn_delete = Button('&Delete')
        self.btn_merge = Button('&Merge')
        self.btn_close = Button('&Close')
        self.btn_reset = Button('&Reset')

        # Connect the buttons to the slots
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_merge.clicked.connect(self.merge_file)
        self.btn_close.clicked.connect(QApplication.quit)
        self.btn_reset.clicked.connect(self.clear_queue)

        # add the buttons to the layout
        self.buttons_layout.addWidget(self.btn_delete, 1, Qt.AlignRight)
        self.buttons_layout.addWidget(self.btn_merge)
        self.buttons_layout.addWidget(self.btn_close)
        self.buttons_layout.addWidget(self.btn_reset)

        # adding the layouts and widgets to the main layout
        self.layout.addLayout(self.output_folder_layout)
        self.layout.addWidget(QLabel("Drop files here:"))
        self.layout.addWidget(self.pdf_list_widget)
        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)

    def _get_saveto_file_path(self):
        file_save_path, _ = QFileDialog.getSaveFileName(self,
                                                        'Save PDF File', os.getcwd(),
                                                        'PDF File (*.pdf)')
        return file_save_path

    @Slot()
    def populate_file_name(self):
        path = self._get_saveto_file_path()
        if path:
            self.output_file.setText(path)

    @Slot()
    def delete_selected(self):
        for item in self.pdf_list_widget.selectedItems():
            self.pdf_list_widget.takeItem(self.pdf_list_widget.row(item))

    @Slot()
    def clear_queue(self):
        self.pdf_list_widget.clear()
        self.output_file.setText('')

    def dialog_message(self, message):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('ASSA PDF Merger')
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(message)
        dlg.show()

    @Slot()
    def merge_file(self):
        if not self.output_file.text():
            self.populate_file_name()
            return
        if self.pdf_list_widget.count() > 0:
            pdf_merger = PdfFileMerger()
            try:
                for i in range(self.pdf_list_widget.count()):
                    pdf_merger.append(self.pdf_list_widget.item(i).text())
                pdf_merger.write(self.output_file.text())
                pdf_merger.close()

                self.pdf_list_widget.clear()
                self.dialog_message('PDF Merge Completed!')
            except Exception as e:
                self.dialog_message(e)
        else:
            self.dialog_message('There are no files to merge')
# class TabSinglePDFWidget


class TabMassivePDFWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.source_folder_layout = QHBoxLayout()
        self.dest_folder_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.right_layout = QVBoxLayout()

        # QLineEdit for output folder and source folder
        self.source_folder = OutputField()
        self.dest_folder = OutputField()
        self.source_folder_layout.addWidget(self.source_folder)
        self.dest_folder_layout.addWidget(self.dest_folder)

        # Creates and adds a QPushButton to browse the source folder
        self.btn_browse_source = Button('From folder')
        self.btn_browse_source.clicked.connect(self.populate_source_file)
        self.source_folder_layout.addWidget(self.btn_browse_source)

        # Creates and adds a QPushButton to browse the destination folder
        self.btn_browse_dest = Button('To folder')
        self.btn_browse_dest.clicked.connect(self.populate_dest_file)
        self.dest_folder_layout.addWidget(self.btn_browse_dest)

        # Creates a button to load files and get the possible order of files
        self.btn_load = Button('Load files')
        self.btn_load.clicked.connect(self.load_files_order)
        self.right_layout.addWidget(self.btn_load)

        # Creates a button to merge the files in the order showed by ListWidget
        self.btn_merge = Button('Merge')
        self.btn_merge.clicked.connect(self.massive_merge)
        self.right_layout.addWidget(self.btn_merge)

        # Creates the ListBox Widget
        self.pdf_order_widget = ListWidget()

        self.layout.addLayout(self.source_folder_layout)
        self.layout.addLayout(self.dest_folder_layout)
        self.layout.addWidget(QLabel("Drag names to set page structure:"))
        self.middle_layout.addWidget(self.pdf_order_widget)
        self.middle_layout.addLayout(self.right_layout)
        self.layout.addLayout(self.middle_layout)
        self.setLayout(self.layout)

    def dialogMessage(self, message, icon):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('ASSA PDF Manager')
        dlg.setIcon(icon)
        dlg.setText(message)
        dlg.show()

    def _get_saveto_path(self):
        path = QFileDialog.getExistingDirectory(self,
                                                'Save files to',
                                                os.getcwd(), )
        return path

    @Slot()
    def populate_source_file(self):
        path = self._get_saveto_path()
        if path:
            self.source_folder.setText(path)

    @Slot()
    def populate_dest_file(self):
        path = self._get_saveto_path()
        if path:
            self.dest_folder.setText(path)

    def load_files(self, source_path):
        """ function receives a source path as parameter. Source path has to be previously checked as dir,
        then loads the file names and split acoording to the regex_pattern
        :returns file names sepparated by regex_pattern and a list of pdf file names """
        # source_path = "/Users/omendoza/GitHub/Python/UnificarPDFs/resources/polizas/caratulas"
        pdf_files = [f for f in os.listdir(source_path) if f.endswith('.pdf')]
        delimiters = "_", " ", "."
        regex_pattern = '|'.join(map(re.escape, delimiters))
        splitted_names = [re.split(regex_pattern, x) for x in pdf_files]
        return splitted_names, pdf_files

    @Slot()
    def load_files_order(self):
        if path.isdir(self.source_folder.text()):
            splitted_names, _ = self.load_files(self.source_folder.text())
            poliza_parts = list(set([x[1] for x in splitted_names]))
            self.pdf_order_widget.addItems(poliza_parts)
        else:
            self.dialogMessage('Source directory is empty or incorrect. '
                               'Please correct or choose a source folder!', QMessageBox.Warning)


    @Slot()
    def massive_merge(self):
        if path.isdir(self.source_folder.text()) and path.isdir(self.dest_folder.text()):
            splitted_names, pdf_files = self.load_files(self.source_folder.text())
            # order_list = [self.pdf_order_widget.findItems('', Qt.MatchRegExp)]
            order_list = [str(self.pdf_order_widget.item(i).text())
                          for i in range(self.pdf_order_widget.count())]
            print(f'order list: {order_list}')
            if order_list:
                polizas = list(set([x[0] for x in splitted_names]))
                print(f'polizas : {polizas}')
                try:
                    for poliza in polizas:
                        pdf_merger = PdfFileMerger()
                        for part in order_list:
                            file_pattern = '_'.join([poliza, part])
                            file_name = [s for s in pdf_files if file_pattern in s]
                            print(f'file_name: {file_name}')
                            if file_name:
                                fullfile_name = path.join(self.source_folder.text(), file_name[0])
                                pdf_merger.append(fullfile_name)

                        file_dest = path.join(self.dest_folder.text(), '.'.join([poliza, 'pdf']))

                        # str(str(self.source_folder.text() + poliza + '.pdf'))
                        print(f'file dest: {file_dest}')
                        # self.setStatusTip(f'{file_dest}')
                        pdf_merger.write(file_dest)
                        pdf_merger.close()
                    self.dialogMessage('Massive Merge Completed', QMessageBox.Information)
                except Exception as e:
                    self.dialogMessage(str(e))
            else:
                self.dialogMessage('Order list is empty, please load files first!',
                                   QMessageBox.Warning)
        else:
            self.dialogMessage('Source or destination directory is not a directory, '
                               'please correct!', QMessageBox.Warning)

        # try:
        #
        # except Exception as e:
        #     self.dialogMessage(str(e))


class MainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # Adding the tabs
        self.mainTab = QTabWidget()
        self.tabSinglePDF = TabSinglePDFWidget()
        self.tabMassivePDF = TabMassivePDFWidget()

        self.mainTab.addTab(self.tabSinglePDF, "Single PDF")
        self.mainTab.addTab(self.tabMassivePDF, "Massive PDF")

        # QWidget Layout
        self.layout = QVBoxLayout()

        # QWidget Label

        # Add widget to the main layout
        self.layout.addWidget(self.mainTab)

        # Add a label for Copyright
        self.CopyRight =  QLabel("Created by Orlando J. Mendoza. Licensed under MIT License.")
        self.CopyRight.setAlignment(Qt.AlignRight)

        self.layout.addWidget(self.CopyRight)

        # Set the layout to the QWidget
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("ASSA PDF Merger")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Status Bar
        self.Status = QStatusBar()
        #self.Status.showMessage("Created by Orlando J. Mendoza. Licensed under MIT License")
        self.setStatusBar(self.Status)

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)



    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    widget = MainWidget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute the application
    sys.exit(app.exec_())
