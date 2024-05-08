import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
    QFileDialog,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtGui import QPixmap
from backend import search_images


class ImageSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Search App")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter search query")
        layout.addWidget(self.query_input)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_images)
        layout.addWidget(search_button)

        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_grid = QGridLayout(self.results_widget)
        self.results_scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll_area)

        central_widget.setLayout(layout)

        # Set the image directory
        self.image_directory = os.getcwd()

    def search_images(self):
        query = self.query_input.text()
        results = search_images(query, self.image_directory)
        print(results)
        self.display_results(results)

    def display_results(self, results):
        # Clear the previous results
        for i in reversed(range(self.results_grid.count())):
            item = self.results_grid.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        row = 0
        col = 0
        for result in results:
            pixmap = QPixmap(result["path"])
            label = QLabel()
            scaled_pixmap = pixmap.scaledToWidth(200)  # Initial scale
            label.setPixmap(scaled_pixmap)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
            self.results_grid.addWidget(label, row, col)
            col += 1
            if col >= 4:  # Adjust this value to set the number of columns
                col = 0
                row += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSearchApp()
    window.show()
    sys.exit(app.exec_())
