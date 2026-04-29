"""
ui/dialog_form.py
Dialog terpisah untuk menambah dan mengedit sesi latihan.
Separation of Concerns: Hanya berisi UI dan event form dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QSpinBox,
    QComboBox, QDateEdit, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from logic.practice_logic import (
    INSTRUMEN_LIST, MOOD_LIST,
    simpan_sesi, edit_sesi, validasi_form
)
from database.db_manager import get_sesi_by_id


class DialogFormSesi(QDialog):
    """Dialog untuk menambah atau mengedit sesi latihan musik."""

    def __init__(self, parent=None, sesi_id=None):
        super().__init__(parent)
        self.sesi_id = sesi_id
        self.is_edit = sesi_id is not None
        self._setup_ui()
        if self.is_edit:
            self._load_data()

    # ------------------------------------------------------------------ UI --
    def _setup_ui(self):
        judul = "✏️  Edit Sesi Latihan" if self.is_edit else "➕  Tambah Sesi Latihan"
        self.setWindowTitle(judul)
        self.setMinimumWidth(480)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # -- Header --
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(64)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        lbl_title = QLabel(judul)
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #4ade80; background: transparent;")
        h_layout.addWidget(lbl_title)
        root.addWidget(header)

        # -- Form --
        form_container = QFrame()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(24, 20, 24, 12)
        form_layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # 1. Tanggal
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd MMMM yyyy")
        self.date_edit.setToolTip("Pilih tanggal sesi latihan")
        form.addRow("📅  Tanggal:", self.date_edit)

        # 2. Instrumen
        self.combo_instrumen = QComboBox()
        self.combo_instrumen.addItems(INSTRUMEN_LIST)
        self.combo_instrumen.setToolTip("Pilih instrumen yang digunakan")
        form.addRow("🎸  Instrumen:", self.combo_instrumen)

        # 3. Materi Latihan
        self.input_materi = QLineEdit()
        self.input_materi.setPlaceholderText("Contoh: Canon in D — fingerstyle")
        self.input_materi.setMaxLength(120)
        self.input_materi.setToolTip("Judul lagu atau materi yang dilatih")
        form.addRow("🎵  Materi Latihan:", self.input_materi)

        # 4. Durasi
        self.spin_durasi = QSpinBox()
        self.spin_durasi.setRange(1, 720)
        self.spin_durasi.setValue(30)
        self.spin_durasi.setSuffix("  menit")
        self.spin_durasi.setToolTip("Berapa lama latihan berlangsung (menit)")
        form.addRow("⏱  Durasi:", self.spin_durasi)

        # 5. Mood
        self.combo_mood = QComboBox()
        self.combo_mood.addItems(MOOD_LIST)
        self.combo_mood.setToolTip("Bagaimana kondisi latihan kamu hari ini?")
        self.combo_mood.currentIndexChanged.connect(self._update_mood_color)
        form.addRow("💭  Mood:", self.combo_mood)

        # 6. Catatan
        self.text_catatan = QTextEdit()
        self.text_catatan.setPlaceholderText(
            "Tuliskan catatan latihan, progress, kesulitan, atau hal yang perlu diingat..."
        )
        self.text_catatan.setFixedHeight(90)
        self.text_catatan.setToolTip("Catatan opsional tentang sesi latihan ini")
        form.addRow("📝  Catatan:", self.text_catatan)

        form_layout.addLayout(form)

        # -- Separator --
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #2d3148;")
        form_layout.addWidget(separator)

        # -- Buttons --
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setObjectName("btnBatal")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reject)

        label_simpan = "💾  Simpan Perubahan" if self.is_edit else "💾  Simpan Sesi"
        self.btn_simpan = QPushButton(label_simpan)
        self.btn_simpan.setObjectName("btnSimpan")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self._on_simpan)
        self.btn_simpan.setDefault(True)

        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_simpan)
        form_layout.addLayout(btn_layout)

        root.addWidget(form_container)
        self._update_mood_color()

    def _update_mood_color(self):
        """Mengubah warna teks ComboBox mood sesuai pilihan."""
        from logic.practice_logic import MOOD_COLOR
        mood = self.combo_mood.currentText()
        color = MOOD_COLOR.get(mood, "#e2e8f0")
        self.combo_mood.setStyleSheet(
            f"QComboBox {{ color: {color}; font-weight: bold; }}"
        )

    # --------------------------------------------------------------- Data --
    def _load_data(self):
        """Mengisi form dengan data sesi yang akan diedit."""
        sesi = get_sesi_by_id(self.sesi_id)
        if not sesi:
            QMessageBox.warning(self, "Error", "Data sesi tidak ditemukan.")
            self.reject()
            return

        self.date_edit.setDate(QDate.fromString(sesi["tanggal"], "yyyy-MM-dd"))

        idx_instrumen = self.combo_instrumen.findText(sesi["instrumen"])
        if idx_instrumen >= 0:
            self.combo_instrumen.setCurrentIndex(idx_instrumen)

        self.input_materi.setText(sesi["materi"])
        self.spin_durasi.setValue(sesi["durasi"])

        idx_mood = self.combo_mood.findText(sesi["mood"])
        if idx_mood >= 0:
            self.combo_mood.setCurrentIndex(idx_mood)

        self.text_catatan.setPlainText(sesi["catatan"] or "")
        self._update_mood_color()

    # ------------------------------------------------------------ Slots --
    def _on_simpan(self):
        """Memvalidasi dan menyimpan data sesi."""
        tanggal    = self.date_edit.date().toString("yyyy-MM-dd")
        instrumen  = self.combo_instrumen.currentText()
        materi     = self.input_materi.text().strip()
        durasi     = self.spin_durasi.value()
        mood       = self.combo_mood.currentText()
        catatan    = self.text_catatan.toPlainText().strip()

        ok, pesan = validasi_form(tanggal, instrumen, materi, durasi)
        if not ok:
            QMessageBox.warning(self, "⚠️  Validasi Gagal", pesan)
            return

        if self.is_edit:
            sukses, msg = edit_sesi(self.sesi_id, tanggal, instrumen, materi, durasi, mood, catatan)
        else:
            sukses, msg = simpan_sesi(tanggal, instrumen, materi, durasi, mood, catatan)

        if sukses:
            self.accept()
        else:
            QMessageBox.critical(self, "❌  Error", msg)
