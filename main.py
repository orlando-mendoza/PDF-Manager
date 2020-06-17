import sys
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QLabel,
                               QMainWindow, QPushButton, QWidget, QTabWidget,
                               QAction)

class centralWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # Adding the tabs
        self.mainTab = QTabWidget()
        self.tabSinglePDF = QWidget()
        self.tabMassivePDF = QWidget()

        self.mainTab.addTab(self.tabSinglePDF, "Single PDF")
        self.mainTab.addTab(self.tabMassivePDF, "Massive PDF")

        # QWidget Layout
        self.layout = QHBoxLayout()

        # Add widget to the main layout
        self.layout.addWidget(self.mainTab)

        # Set the layout to the QWidget
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("ASSA PDF Merger")

        #Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

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
    widget = centralWidget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute the application
    sys.exit(app.exec_())
