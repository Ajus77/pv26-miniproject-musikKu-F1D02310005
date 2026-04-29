"""
main.py
Titik masuk utama aplikasi MusikKu - Music Practice Tracker.
Menginisialisasi database, memuat stylesheet, dan menampilkan jendela utama.
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db_manager import init_db
from ui.main_window import MainWindow

QSS_PATH = os.path.join(BASE_DIR, "styles", "style.qss")


def load_stylesheet(app: QApplication) -> None:
    """Memuat stylesheet QSS dari file eksternal."""
    if os.path.exists(QSS_PATH):
        with open(QSS_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[Peringatan] File stylesheet tidak ditemukan: {QSS_PATH}")


def main():
    # Inisialisasi database (buat tabel jika belum ada)
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("MusikKu")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Pemrograman Visual")

    # Set font default
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Muat stylesheet dari file eksternal
    load_stylesheet(app)

    # Tampilkan jendela utama
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
