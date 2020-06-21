import os
import sys
import io

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QUrl

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ';' + os.environ['PATH']
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, \
                            QLineEdit, QPushButton, QVBoxLayout, \
                            QHBoxLayout, QAbstractItemView, QLabel, \
                            QGridLayout, QDialog, QFileDialog, \
                            QMessageBox, QTabWidget
from PyQt5.QtGui import QIcon
from PyPDF2 import PdfFileMerger


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        self.setStyleSheet('font-size: 25px;')
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


class outputField(QLineEdit):
    def __init__(self):
        super().__init__()
        self.height = 55
        self.setStyleSheet('font-size: 30px;')
        self.setFixedHeight(self.height)

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


class button(QPushButton):
    def __init__(self, label_text):
        super().__init__()
        self.setText(label_text)
        self.setStyleSheet('''
            font-size: 30px;
            width: 180px;
            height: 50px;
        ''')

class PDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ASSA PDF Merge Utility')
        self.setWindowIcon(QIcon(resource_path(r'pdf.png')))
        self.resize(1280, 790)
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        self.mainTab = QTabWidget()
        self.tabSinglePDF = QWidget()
        self.tabMassivePDFMerger = QWidget()

        self.mainTab.addTab(self.tabSinglePDF, "")
        self.mainTab.addTab(self.tabMassivePDFMerger, "")


        # Rows for the single PDF Tab
        outputFolderRow = QHBoxLayout()
        btnLayout = QHBoxLayout()

        # Rows for the Massive Merger Tab
        sourceDirRow = QHBoxLayout()
        targetDirRow = QHBoxLayout()


        mainLayout.addWidget(self.mainTab)

        self.outputFile = outputField()
        outputFolderRow.addWidget(self.outputFile)

        # browse button
        self.btnBrowseOutputFile = button('&Guardar en')
        self.btnBrowseOutputFile.clicked.connect(self.populateFileName)
        outputFolderRow.addWidget(self.btnBrowseOutputFile)

        # listbox widget
        self.pdfListWidget = ListWidget(self)

        # Buttons
        self.buttonDeleteSelect = button('&Borrar')
        self.buttonDeleteSelect.clicked.connect(self.deleteSelected)
        btnLayout.addWidget(self.buttonDeleteSelect, 1, Qt.AlignRight)

        self.buttonMerge = button('&Unificar')
        self.buttonMerge.cli°cked.connect(self.mergeFile)
        btnLayout.addWidget(self.buttonMerge)

        self.buttonClose = button('&Cerrar')
        self.buttonClose.clicked.connect(QApplication.quit)
        btnLayout.addWidget(self.buttonClose)

        self.buttonReset = button('&Reset')
        self.buttonReset .clicked.connect(self.clearQueue)
        btnLayout.addWidget(self.buttonReset)


        # Adding tabs to mainLayout
        mainLayout.addWidget(self.mainTab)


        mainLayout.addLayout(outputFolderRow)
        mainLayout.addWidget(self.pdfListWidget)
        mainLayout.addLayout(btnLayout)
        self.setLayout(mainLayout)


    def deleteSelected(self):
        for item in self.pdfListWidget.selectedItems():
            self.pdfListWidget.takeItem(self.pdfListWidget.row(item))


    def clearQueue(self):
        self.pdfListWidget.clear()
        self.outputFile.setText('')


    def dialogMessage(self, message):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('PDF Manager')
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(message)
        dlg.show()


    def _getSaveFilePath(self):
        file_save_path, _ = QFileDialog.getSaveFileName(self, \
                                                        'Save PDF file', os.getcwd(),\
                                                        'PDF File (*.pdf)')
        return file_save_path


    def populateFileName(self):
        path = self._getSaveFilePath()
        if path:
            self.outputFile.setText(path)


    def mergeFile(self):
        if not self.outputFile.text():
            self.populateFileName()
            return

        if self.pdfListWidget.count() > 0:
            pdfMerger = PdfFileMerger()
            try:
                for i in range(self.pdfListWidget.count()):
                    pdfMerger.append(self.pdfListWidget.item(i).text())
                pdfMerger.write(self.outputFile.text())
                pdfMerger.close()

                self.pdfListWidget.clear()
                self.dialogMessage('PDF Merge Completed!')
            except Exception as e:
                self.dialogMessage(e)
        else:
            self.dialogMessage('No hay archivos para unificar')


app = QApplication(sys.argv)
app.setStyle('fusion')

pdfApp = PDFApp()
pdfApp.show()

sys.exit(app.exec_())
