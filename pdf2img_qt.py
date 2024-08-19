import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QCheckBox, QMessageBox, QSpinBox, QDialog, QScrollArea, QSlider,QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon, QImage, qRgba
from PyQt5.QtCore import Qt, pyqtSignal
import subprocess
import os
import platform
import webbrowser

class PreviewDialog(QDialog):
    zoomChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Preview')

        layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)

        self.scroll_area.setWidget(self.preview_label)
        layout.addWidget(self.scroll_area)

        slider_layout = QHBoxLayout()
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.valueChanged.connect(self.changeZoom)
        slider_layout.addWidget(self.zoom_slider)
        layout.addLayout(slider_layout)

    def changeZoom(self, value):
        self.zoomChanged.emit(value)

    def setPixmap(self, pixmap):
        scaled_pixmap = pixmap.scaledToWidth(pixmap.width() * (self.zoom_slider.value() / 100.0))
        self.preview_label.setPixmap(scaled_pixmap)


class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF to Image Converter')
        try:
            self.setWindowIcon(QIcon('icon.ico'))
        except:
            pass
        if platform.system()=='Windows':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        grid_layout = QGridLayout()
        row = 0

        # PDF selection
        grid_layout.addWidget(QLabel("Select PDF:"), row, 0)
        self.pdf_entry = QLineEdit()
        grid_layout.addWidget(self.pdf_entry, row, 1)
        browse_pdf_button = QPushButton("Browse", clicked=self.browse_pdf)
        grid_layout.addWidget(browse_pdf_button, row, 2)
        row += 1

        # Preview
        preview_button = QPushButton("Preview", clicked=self.preview_first_page)
        grid_layout.addWidget(preview_button, row, 1)
        row += 1

        # Output
        grid_layout.addWidget(QLabel("Output Format:"), row, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpeg", "tiff", "pdf", "ps", "eps", "svg"])
        self.format_combo.setCurrentIndex(0)
        grid_layout.addWidget(self.format_combo, row, 1)
        row += 1

        grid_layout.addWidget(QLabel("Output Prefix:"), row, 0)
        self.output_entry = QLineEdit()
        grid_layout.addWidget(self.output_entry, row, 1)
        browse_output_button = QPushButton("Browse", clicked=self.browse_output)
        grid_layout.addWidget(browse_output_button, row, 2)
        row += 1

        # DPI
        grid_layout.addWidget(QLabel("Resolution (DPI):"), row, 0)
        self.resolution_spinbox = QSpinBox()
        self.resolution_spinbox.setRange(1, 10000)
        self.resolution_spinbox.setValue(150)
        grid_layout.addWidget(self.resolution_spinbox, row, 1)
        row += 1

        # Scale
        grid_layout.addWidget(QLabel("Scale To (pixels):"), row, 0)
        self.scale_to_spinbox = QSpinBox()
        self.scale_to_spinbox.setRange(0, 10000)
        self.scale_to_spinbox.setValue(0)
        grid_layout.addWidget(self.scale_to_spinbox, row, 1)
        row += 1

        # Crop
        grid_layout.addWidget(QLabel("Crop X:"), row, 0)
        self.crop_x_spinbox = QSpinBox()
        self.crop_x_spinbox.setRange(0, 10000)
        grid_layout.addWidget(self.crop_x_spinbox, row, 1)
        row += 1
        grid_layout.addWidget(QLabel("Crop Y:"), row, 0)
        self.crop_y_spinbox = QSpinBox()
        self.crop_y_spinbox.setRange(0, 10000)
        grid_layout.addWidget(self.crop_y_spinbox, row, 1)
        row += 1
        grid_layout.addWidget(QLabel("Crop W:"), row, 0)
        self.crop_w_spinbox = QSpinBox()
        self.crop_w_spinbox.setRange(0, 10000)
        grid_layout.addWidget(self.crop_w_spinbox, row, 1)
        row += 1
        grid_layout.addWidget(QLabel("Crop H:"), row, 0)
        self.crop_h_spinbox = QSpinBox()
        self.crop_h_spinbox.setRange(0, 10000)
        grid_layout.addWidget(self.crop_h_spinbox, row, 1)
        row += 1

        # Single
        self.single_file_check = QCheckBox("-singlefile")
        grid_layout.addWidget(self.single_file_check, row, 1)
        row += 1

        # Center
        self.nocenter_check = QCheckBox("-nocenter")
        grid_layout.addWidget(self.nocenter_check, row, 1)
        row += 1

        layout.addLayout(grid_layout)

        convert_button = QPushButton("Convert", clicked=self.convert_pdf)
        layout.addWidget(convert_button)

        check_pdftocairo_button = QPushButton("Check installation", clicked=self.check_pdftocairo)
        layout.addWidget(check_pdftocairo_button)

        help_button = QPushButton("Help", clicked=self.show_help)
        layout.addWidget(help_button)

        self.status_label = QLabel("", styleSheet="color: blue;")
        layout.addWidget(self.status_label)

        self.resize(600, 400)
        self.show()

    def check_pdftocairo(self):
        try:
            subprocess.run(["pdftocairo", "-v"], check=True, stdout=subprocess.PIPE)
            self.status_label.setText("pdftocairo is already installed.")
        except subprocess.CalledProcessError:
            system = platform.system()
            if system == 'Linux':
                install_command = ["sudo", "apt-get", "install", "-y", "poppler-utils"]
            elif system == 'Darwin':  # macOS
                install_command = ["brew", "install", "poppler"]
            elif system == 'Windows':
                QMessageBox.information(self, "Installation Required",
                                        "Please download and install Poppler for Windows from the link below.\n"
                                        "https://github.com/oschwartz10612/poppler-windows")
                webbrowser.open("https://github.com/oschwartz10612/poppler-windows")
                return
            else:
                self.status_label.setText("Unsupported operating system.")
                return

            try:
                subprocess.run(install_command, check=True)
                self.status_label.setText("Poppler (including pdftocairo) has been installed successfully.")
            except subprocess.CalledProcessError as e:
                self.status_label.setText(f"Installation failed: {e}")

    def browse_pdf(self):
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF files (*.pdf)")
        if pdf_path:
            self.pdf_entry.setText(pdf_path)

    def browse_output(self):
        output_format = self.format_combo.currentText()
        default_extension = f".{output_format}"
        default_name = os.path.splitext(os.path.basename(self.pdf_entry.text()))[0]
        output_path, _ = QFileDialog.getSaveFileName(self, "Save As", f"{default_name}{default_extension}")
        if output_path:
            self.output_entry.setText(output_path)

    def convert_pdf(self):
        pdf_file = self.pdf_entry.text()
        output_prefix = self.output_entry.text()
        output_format = self.format_combo.currentText()
        scale_to = self.scale_to_spinbox.value()
        resolution = self.resolution_spinbox.value()
        crop_x = self.crop_x_spinbox.value()
        crop_y = self.crop_y_spinbox.value()
        crop_w = self.crop_w_spinbox.value()
        crop_h = self.crop_h_spinbox.value()
        single_file = self.single_file_check.isChecked()
        nocenter = self.nocenter_check.isChecked()

        if not pdf_file or not output_prefix:
            self.status_label.setText("Please select a PDF file and provide an output prefix.")
            return

        command = ["pdftocairo", f"-{output_format}"]
        if scale_to:
            command.extend(["-scale-to", str(scale_to)])
        if resolution:
            command.extend(["-r", str(resolution)])
        if crop_x or crop_y or crop_w or crop_h:
            command.extend(["-x", str(crop_x), "-y", str(crop_y), "-W", str(crop_w), "-H", str(crop_h)])
        if single_file:
            command.append("-singlefile")
        if nocenter:
            command.append("-nocenter")
        command.extend([pdf_file, output_prefix])

        try:
            subprocess.run(command, check=True)
            self.status_label.setText("Conversion successful.")
        except subprocess.CalledProcessError as e:
            self.status_label.setText(f"Conversion failed: {e}")


    def preview_first_page(self):
        pdf_file = self.pdf_entry.text()

        if not pdf_file:
            self.status_label.setText("Please select a PDF file.")
            return

        temp_png_file = "temp_preview"
        command = ["pdftocairo", "-singlefile", "-png", pdf_file, temp_png_file]

        try:
            subprocess.run(command, check=True)
            
            pixmap = QPixmap(f"{temp_png_file}.png")
            self.preview_dialog = PreviewDialog(self)
            self.preview_dialog.setPixmap(pixmap)
            self.preview_dialog.zoomChanged.connect(lambda value: self.preview_dialog.setPixmap(pixmap.scaledToWidth(pixmap.width() * (value / 100.0))))
            self.preview_dialog.exec_()
            self.status_label.setText("First page preview loaded.")
        except subprocess.CalledProcessError as e:
            self.status_label.setText(f"Preview failed: {e}")
        finally:
            if os.path.exists(f"{temp_png_file}.png"):
                os.remove(f"{temp_png_file}.png")

    def show_help(self):
        help_text = "PDF to Image Converter Usage:\n\n"
        help_text += "1. Select the PDF file you want to convert using the Browse button.\n"
        help_text += "2. Choose the output format from the dropdown menu.\n"
        help_text += "3. Provide a prefix for the output file(s) in the Output Prefix field.\n"
        help_text += "4. Optionally, set the resolution, scale, or cropping parameters.\n"
        help_text += "   - Resolution (DPI): Enter the desired DPI for the output image.\n"
        help_text += "   - Scale To (pixels): Scale the output to a specific pixel size.\n"
        help_text += "   - Crop (X Y W H): Define the area of the PDF page to be cropped.\n"
        help_text += "5. Check the -singlefile box to output only the first page.\n"
        help_text += "6. Check the -nocenter box to disable automatic centering of the output.\n"
        help_text += "7. Click the Convert button to start the conversion process.\n"
        help_text += "8. The status message will indicate whether the conversion was successful."

        QMessageBox.information(self, "Help", help_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFConverterApp()
    sys.exit(app.exec_())
