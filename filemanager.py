import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeView, QFileSystemModel, QPushButton, QMessageBox, QTabWidget, QLineEdit, QAbstractItemView, QFileDialog
from PyQt5.QtCore import Qt,  QItemSelectionModel


class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Manager")
        self.resize(800, 600)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.addTab(TabView(os.path.expanduser("~"), self), "Home")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def add_tab(self, path):
        tab = TabView(path, self)
        tab_index = self.tab_widget.addTab(tab, os.path.basename(path))
        self.tab_widget.setCurrentIndex(tab_index)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            widget.deleteLater()
            self.tab_widget.removeTab(index)


class TabView(QWidget):
    def __init__(self, path, file_manager):
        super().__init__()
        self.path = path
        self.file_manager = file_manager
        self.history = [self.path]  # Store history of visited directories

        self.model = QFileSystemModel()
        self.model.setRootPath(self.path)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.path))
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)  # Allow selecting multiple files
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)  # Select entire row
        self.tree_view.doubleClicked.connect(self.directory_double_clicked)
        self.tree_view.clicked.connect(self.file_clicked)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.textChanged.connect(self.search_files)

        self.btn_copy = QPushButton("Copy")
        self.btn_paste = QPushButton("Paste")
        self.btn_delete = QPushButton("Delete")
        self.btn_back = QPushButton("Back")
        self.btn_open_new_tab = QPushButton("Open in New Tab")

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.tree_view)
        layout.addWidget(self.btn_copy)
        layout.addWidget(self.btn_paste)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_open_new_tab)

        self.setLayout(layout)

        self.btn_copy.clicked.connect(self.copy_file)
        self.btn_paste.clicked.connect(self.paste_file)
        self.btn_delete.clicked.connect(self.delete_file)
        self.btn_back.clicked.connect(self.go_back)
        self.btn_open_new_tab.clicked.connect(self.open_in_new_tab)

        self.copy_sources = []

    def directory_double_clicked(self, index):
        directory_path = self.model.filePath(index)
        if os.path.isdir(directory_path):
            self.tree_view.setRootIndex(self.model.index(directory_path))
            self.history.append(directory_path)

    def file_clicked(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.tree_view.clearSelection()
            self.tree_view.selectionModel().select(index, QItemSelectionModel.Select)

    def go_back(self):
        if len(self.history) > 1:  # Check if history has more than one entry
            self.history.pop()  # Remove current directory from history
            prev_directory = self.history[-1]  # Get the previous directory
            self.tree_view.setRootIndex(self.model.index(prev_directory))

    def open_in_new_tab(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            directory_path = self.model.filePath(index)
            if os.path.isdir(directory_path):
                self.file_manager.add_tab(directory_path)

    def search_files(self, text):
        if text:
            filter_string = f"*{text}*"
            self.model.setNameFilters([filter_string])
        else:
            self.model.setNameFilters([])

    def copy_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return
        
        self.copy_sources = set()

        for index in selected_indexes:
            if index.isValid():
                file_path = self.model.filePath(index)
                self.copy_sources.add(file_path)

        QMessageBox.information(self, "Copy", f"{len(self.copy_sources)} files selected for copying.")

    def paste_file(self):
        if not self.copy_sources:
            return

        # Get the current location of the tab
        dest_path = self.model.rootPath()
        if not dest_path:
            QMessageBox.warning(self, "Error", "No destination selected.")
            return

        if os.path.isdir(dest_path):
            try:
                for source in self.copy_sources:
                    shutil.copy(source, dest_path)
                QMessageBox.information(self, "Paste", f"{len(self.copy_sources)} files pasted to '{dest_path}'.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to paste files: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Destination is not a directory.")
        self.copy_sources = set()



    def delete_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return
        
        files_to_delete = set()

        for index in selected_indexes:
            if index.isValid():
                file_path = self.model.filePath(index)
                files_to_delete.add(file_path)

        confirm_message = f"Are you sure you want to delete {len(files_to_delete)} selected files/directories?"
        reply = QMessageBox.question(self, 'Delete', confirm_message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        try:
                            shutil.rmtree(file_path)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Failed to delete directory '{file_path}': {str(e)}")
                    else:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Failed to delete file '{file_path}': {str(e)}")
            QMessageBox.information(self, "Delete", f"{len(files_to_delete)} files/directories deleted.")
        else:
            QMessageBox.information(self, "Delete", "Operation canceled.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_manager = FileManager()
    file_manager.show()
    sys.exit(app.exec_())
