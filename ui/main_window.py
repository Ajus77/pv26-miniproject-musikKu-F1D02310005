"""
ui/main_window.py
Jendela utama aplikasi MusikKu - Music Practice Tracker.
Separation of Concerns: Hanya berisi definisi dan logika UI utama.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QFrame, QHeaderView, QMessageBox,
    QTabWidget, QStatusBar, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QAction, QColor

from logic.practice_logic import (
    ambil_semua_sesi, hapus_sesi, ambil_statistik,
    INSTRUMEN_LIST, MOOD_COLOR, format_durasi
)
from ui.dialog_form import DialogFormSesi

# ---------------------------------------------------------------- Konstanta --
NAMA_MAHASISWA = "Bagus Esa Wijaya Kusuma"
NIM            = "F1D02310005"
NAMA_APLIKASI  = "MusikKu"
VERSI          = "1.0.0"


class MainWindow(QMainWindow):
    """Jendela utama aplikasi Music Practice Tracker."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🎵  {NAMA_APLIKASI} — Music Practice Tracker")
        self.setMinimumSize(960, 640)
        self.resize(1100, 700)
        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()
        self.refresh_data()

    # ---------------------------------------------------------------- Menu --
    def _setup_menu(self):
        menubar = self.menuBar()

        # Menu File
        menu_file = menubar.addMenu("File")
        act_refresh = QAction("🔄  Refresh Data", self)
        act_refresh.setShortcut("F5")
        act_refresh.triggered.connect(self.refresh_data)
        menu_file.addAction(act_refresh)
        menu_file.addSeparator()
        act_keluar = QAction("🚪  Keluar", self)
        act_keluar.setShortcut("Ctrl+Q")
        act_keluar.triggered.connect(self.close)
        menu_file.addAction(act_keluar)

        # Menu Sesi
        menu_sesi = menubar.addMenu("Sesi")
        act_tambah = QAction("➕  Tambah Sesi Baru", self)
        act_tambah.setShortcut("Ctrl+N")
        act_tambah.triggered.connect(self._on_tambah)
        menu_sesi.addAction(act_tambah)
        act_edit = QAction("✏️  Edit Sesi Terpilih", self)
        act_edit.setShortcut("Ctrl+E")
        act_edit.triggered.connect(self._on_edit)
        menu_sesi.addAction(act_edit)
        act_hapus = QAction("🗑  Hapus Sesi Terpilih", self)
        act_hapus.setShortcut("Delete")
        act_hapus.triggered.connect(self._on_hapus)
        menu_sesi.addAction(act_hapus)

        # Menu Bantuan
        menu_bantuan = menubar.addMenu("Bantuan")
        act_tentang = QAction("ℹ️  Tentang Aplikasi", self)
        act_tentang.triggered.connect(self._show_tentang)
        menu_bantuan.addAction(act_tentang)

    # ------------------------------------------------------------------ UI --
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header
        root_layout.addWidget(self._build_header())

        # Tab utama
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(12, 8, 12, 8)
        tab_riwayat = self._build_tab_riwayat()
        tab_statistik = self._build_tab_statistik()
        self.tabs.addTab(tab_riwayat,   "📋  Riwayat Latihan")
        self.tabs.addTab(tab_statistik, "📊  Statistik")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(12, 8, 12, 8)
        wl.addWidget(self.tabs)
        root_layout.addWidget(wrapper)

    def _build_header(self):
        """Membangun panel header aplikasi."""
        frame = QFrame()
        frame.setObjectName("headerFrame")
        frame.setFixedHeight(72)

        h = QHBoxLayout(frame)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(16)

        # Logo / Judul
        v_title = QVBoxLayout()
        v_title.setSpacing(0)
        lbl_judul = QLabel(f"🎵  {NAMA_APLIKASI}")
        lbl_judul.setObjectName("labelJudul")
        lbl_sub = QLabel("Music Practice Tracker")
        lbl_sub.setObjectName("labelSubjudul")
        v_title.addWidget(lbl_judul)
        v_title.addWidget(lbl_sub)
        h.addLayout(v_title)
        h.addStretch()

        # Identitas mahasiswa (tidak bisa diedit)
        lbl_identitas = QLabel(f"👤  {NAMA_MAHASISWA}  |  NIM: {NIM}")
        lbl_identitas.setObjectName("labelIdentitas")
        lbl_identitas.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        h.addWidget(lbl_identitas)

        return frame

    # -------------------------------------------------- Tab Riwayat Latihan --
    def _build_tab_riwayat(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 8, 4, 4)
        layout.setSpacing(10)

        # Toolbar (filter + tombol aksi)
        layout.addWidget(self._build_toolbar())

        # Tabel data
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tanggal", "Instrumen", "Materi Latihan",
            "Durasi", "Mood", "Catatan", "Dicatat"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnHidden(0, True)   # sembunyikan kolom ID
        self.table.setColumnHidden(7, True)   # sembunyikan kolom created_at

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed);        self.table.setColumnWidth(1, 130)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed);        self.table.setColumnWidth(2, 150)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed);        self.table.setColumnWidth(4, 90)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed);        self.table.setColumnWidth(5, 180)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self.table)

        # Label info jumlah baris
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self.lbl_info)

        return widget

    def _build_toolbar(self):
        """Membangun baris toolbar filter dan tombol aksi."""
        frame = QFrame()
        h = QHBoxLayout(frame)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        # Filter instrumen
        lbl_filter = QLabel("Filter:")
        lbl_filter.setStyleSheet("color: #64748b; font-size: 12px;")
        self.combo_filter = QComboBox()
        self.combo_filter.addItem("Semua Instrumen")
        self.combo_filter.addItems(INSTRUMEN_LIST)
        self.combo_filter.setFixedWidth(180)
        self.combo_filter.currentIndexChanged.connect(self.refresh_data)

        h.addWidget(lbl_filter)
        h.addWidget(self.combo_filter)
        h.addStretch()

        # Tombol aksi
        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btnRefresh")
        btn_refresh.setFixedSize(QSize(36, 36))
        btn_refresh.setToolTip("Refresh data (F5)")
        btn_refresh.clicked.connect(self.refresh_data)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_tambah = QPushButton("➕  Tambah Sesi")
        btn_tambah.setObjectName("btnTambah")
        btn_tambah.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tambah.clicked.connect(self._on_tambah)

        btn_edit = QPushButton("✏️  Edit")
        btn_edit.setObjectName("btnEdit")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(self._on_edit)

        btn_hapus = QPushButton("🗑  Hapus")
        btn_hapus.setObjectName("btnHapus")
        btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hapus.clicked.connect(self._on_hapus)

        h.addWidget(btn_refresh)
        h.addWidget(btn_tambah)
        h.addWidget(btn_edit)
        h.addWidget(btn_hapus)

        return frame

    # -------------------------------------------------- Tab Statistik --
    def _build_tab_statistik(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 12, 4, 4)
        layout.setSpacing(16)

        # Baris kartu ringkasan
        row_cards = QHBoxLayout()
        row_cards.setSpacing(12)

        self.card_total_sesi  = self._stat_card("Total Sesi", "0",      "📅")
        self.card_total_durasi = self._stat_card("Total Durasi", "0 menit", "⏱")
        self.card_instrumen   = self._stat_card("Instrumen", "—",       "🎸")

        row_cards.addWidget(self.card_total_sesi[0])
        row_cards.addWidget(self.card_total_durasi[0])
        row_cards.addWidget(self.card_instrumen[0])
        layout.addLayout(row_cards)

        # Tabel per instrumen
        lbl = QLabel("📊  Rincian Per Instrumen")
        lbl.setStyleSheet("color: #4ade80; font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)

        self.table_stat = QTableWidget()
        self.table_stat.setColumnCount(3)
        self.table_stat.setHorizontalHeaderLabels(["Instrumen", "Jumlah Sesi", "Total Durasi"])
        self.table_stat.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_stat.verticalHeader().setVisible(False)
        self.table_stat.horizontalHeader().setStretchLastSection(True)
        self.table_stat.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.table_stat)

        layout.addStretch()
        return widget

    def _stat_card(self, judul, nilai, ikon):
        """Membuat widget kartu statistik."""
        frame = QFrame()
        frame.setObjectName("statFrame")
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frame.setFixedHeight(100)

        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(4)

        lbl_ikon_judul = QLabel(f"{ikon}  {judul}")
        lbl_ikon_judul.setObjectName("labelStatJudul")

        lbl_nilai = QLabel(nilai)
        lbl_nilai.setObjectName("labelStatCard")

        v.addWidget(lbl_ikon_judul)
        v.addWidget(lbl_nilai)
        return frame, lbl_nilai

    # ---------------------------------------------------------------- Status --
    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Selamat datang di MusikKu!")

    # ---------------------------------------------------------------- Slots --
    def _on_tab_changed(self, index):
        if index == 1:   # Tab Statistik
            self._refresh_statistik()

    def _on_tambah(self):
        dialog = DialogFormSesi(self)
        if dialog.exec():
            self.refresh_data()
            self.statusbar.showMessage("✅  Sesi latihan baru berhasil ditambahkan.")

    def _on_edit(self):
        sesi_id = self._get_selected_id()
        if sesi_id is None:
            QMessageBox.information(self, "Info", "Pilih sesi latihan yang ingin diedit.")
            return
        dialog = DialogFormSesi(self, sesi_id=sesi_id)
        if dialog.exec():
            self.refresh_data()
            self.statusbar.showMessage("✅  Sesi latihan berhasil diperbarui.")

    def _on_hapus(self):
        sesi_id = self._get_selected_id()
        if sesi_id is None:
            QMessageBox.information(self, "Info", "Pilih sesi latihan yang ingin dihapus.")
            return

        row = self.table.currentRow()
        materi = self.table.item(row, 3).text() if self.table.item(row, 3) else "sesi ini"

        # Dialog konfirmasi (QMessageBox)
        konfirmasi = QMessageBox(self)
        konfirmasi.setWindowTitle("🗑  Konfirmasi Hapus")
        konfirmasi.setText(f"Apakah kamu yakin ingin menghapus sesi latihan:\n\n\"{materi}\"?")
        konfirmasi.setInformativeText("Tindakan ini tidak dapat dibatalkan.")
        konfirmasi.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        konfirmasi.setDefaultButton(QMessageBox.StandardButton.No)
        konfirmasi.button(QMessageBox.StandardButton.Yes).setText("Ya, Hapus")
        konfirmasi.button(QMessageBox.StandardButton.No).setText("Batal")

        if konfirmasi.exec() == QMessageBox.StandardButton.Yes:
            hapus_sesi(sesi_id)
            self.refresh_data()
            self.statusbar.showMessage("🗑  Sesi latihan berhasil dihapus.")

    def _show_tentang(self):
        """Menampilkan dialog Tentang Aplikasi."""
        msg = QMessageBox(self)
        msg.setWindowTitle("ℹ️  Tentang Aplikasi")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(f"""
            <div style='font-family: Segoe UI; font-size: 13px;'>
            <h2 style='color: #4ade80; margin:0;'>🎵 {NAMA_APLIKASI}</h2>
            <p style='color: #94a3b8; margin-top:4px; font-size: 11px;'>Versi {VERSI}</p>
            <hr style='border-color: #2d3148;'>
            <p><b>Deskripsi:</b><br>
            Aplikasi untuk mencatat dan melacak sesi latihan musik harianmu.
            Catat instrumen, materi, durasi, mood, dan lihat progresmu dari waktu ke waktu!</p>
            <hr style='border-color: #2d3148;'>
            <p><b>Dikembangkan oleh:</b><br>
            👤 <b>{NAMA_MAHASISWA}</b><br>
            🎓 NIM: <b>{NIM}</b></p>
            <p style='color: #64748b; font-size: 11px;'>
            Tugas Mini Proyek UTS — Pemrograman Visual<br>
            Dibangun dengan Python &amp; PySide6</p>
            </div>
        """)
        msg.exec()

    # ---------------------------------------------------------- Helpers --
    def _get_selected_id(self):
        """Mengambil ID sesi dari baris tabel yang dipilih."""
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        return int(item.text())

    # ----------------------------------------------------------- Refresh --
    def refresh_data(self):
        """Mengambil ulang data dari database dan mengisi ulang tabel."""
        filter_val = self.combo_filter.currentText()
        if filter_val == "Semua Instrumen":
            filter_val = None

        sesi_list = ambil_semua_sesi(filter_instrumen=filter_val)
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for sesi in sesi_list:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID (tersembunyi)
            item_id = QTableWidgetItem(str(sesi["id"]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_id)

            # Tanggal (format tampilan)
            from PySide6.QtCore import QDate
            tgl = QDate.fromString(sesi["tanggal"], "yyyy-MM-dd")
            item_tgl = QTableWidgetItem(tgl.toString("dd MMM yyyy"))
            item_tgl.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_tgl)

            # Instrumen
            item_inst = QTableWidgetItem(sesi["instrumen"])
            item_inst.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_inst)

            # Materi
            self.table.setItem(row, 3, QTableWidgetItem(sesi["materi"]))

            # Durasi
            item_dur = QTableWidgetItem(format_durasi(sesi["durasi"]))
            item_dur.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, item_dur)

            # Mood (dengan warna)
            item_mood = QTableWidgetItem(sesi["mood"])
            item_mood.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            color = MOOD_COLOR.get(sesi["mood"], "#e2e8f0")
            item_mood.setForeground(QColor(color))
            self.table.setItem(row, 5, item_mood)

            # Catatan
            catatan = sesi["catatan"] or "—"
            self.table.setItem(row, 6, QTableWidgetItem(catatan))

            # Created at (tersembunyi)
            self.table.setItem(row, 7, QTableWidgetItem(sesi["created_at"] or ""))

        self.table.setSortingEnabled(True)
        jumlah = self.table.rowCount()
        self.lbl_info.setText(f"Menampilkan {jumlah} sesi latihan")
        self.statusbar.showMessage(f"Data diperbarui — {jumlah} sesi ditemukan.")

    def _refresh_statistik(self):
        """Memperbarui tampilan kartu dan tabel statistik."""
        stat = ambil_statistik()

        # Update kartu
        self.card_total_sesi[1].setText(str(stat["total_sesi"]))
        self.card_total_durasi[1].setText(stat["label_durasi"])

        top_instrumen = stat["per_instrumen"][0]["instrumen"] if stat["per_instrumen"] else "—"
        self.card_instrumen[1].setText(top_instrumen)

        # Update tabel statistik
        self.table_stat.setRowCount(0)
        for data in stat["per_instrumen"]:
            row = self.table_stat.rowCount()
            self.table_stat.insertRow(row)

            self.table_stat.setItem(row, 0, QTableWidgetItem(data["instrumen"]))
            item_jml = QTableWidgetItem(str(data["jumlah"]))
            item_jml.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_stat.setItem(row, 1, item_jml)

            item_dur = QTableWidgetItem(format_durasi(data["total_menit"]))
            item_dur.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_stat.setItem(row, 2, item_dur)

        self.table_stat.resizeColumnsToContents()
