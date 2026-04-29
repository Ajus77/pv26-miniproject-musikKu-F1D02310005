"""
logic/practice_logic.py
Modul logika bisnis aplikasi Music Practice Tracker.
Separation of Concerns: Memisahkan logika dari UI dan database.
"""

from database import db_manager


INSTRUMEN_LIST = [
    "Gitar Akustik",
    "Gitar Elektrik",
    "Gitar Bass",
    "Piano / Keyboard",
    "Drum / Perkusi",
    "Biola",
    "Ukulele",
    "Vokal",
    "Flute",
    "Lainnya",
]

MOOD_LIST = [
    "😄 Sangat Semangat",
    "🙂 Semangat",
    "😐 Biasa Saja",
    "😔 Kurang Fokus",
    "😩 Tidak Produktif",
]

MOOD_COLOR = {
    "😄 Sangat Semangat": "#4ade80",
    "🙂 Semangat":        "#86efac",
    "😐 Biasa Saja":      "#fbbf24",
    "😔 Kurang Fokus":    "#fb923c",
    "😩 Tidak Produktif": "#f87171",
}


def validasi_form(tanggal, instrumen, materi, durasi):
    """
    Memvalidasi input form sebelum disimpan.
    Mengembalikan (True, '') jika valid, atau (False, pesan_error).
    """
    if not tanggal:
        return False, "Tanggal tidak boleh kosong."
    if not instrumen:
        return False, "Instrumen tidak boleh kosong."
    if not materi or len(materi.strip()) < 2:
        return False, "Materi latihan minimal 2 karakter."
    if durasi <= 0:
        return False, "Durasi latihan harus lebih dari 0 menit."
    if durasi > 720:
        return False, "Durasi latihan tidak boleh lebih dari 720 menit (12 jam)."
    return True, ""


def simpan_sesi(tanggal, instrumen, materi, durasi, mood, catatan):
    """Memvalidasi lalu menyimpan sesi latihan baru."""
    ok, pesan = validasi_form(tanggal, instrumen, materi, durasi)
    if not ok:
        return False, pesan
    db_manager.tambah_sesi(tanggal, instrumen, materi, durasi, mood, catatan)
    return True, "Sesi latihan berhasil disimpan!"


def edit_sesi(sesi_id, tanggal, instrumen, materi, durasi, mood, catatan):
    """Memvalidasi lalu memperbarui sesi latihan yang ada."""
    ok, pesan = validasi_form(tanggal, instrumen, materi, durasi)
    if not ok:
        return False, pesan
    db_manager.update_sesi(sesi_id, tanggal, instrumen, materi, durasi, mood, catatan)
    return True, "Sesi latihan berhasil diperbarui!"


def hapus_sesi(sesi_id):
    """Menghapus sesi latihan berdasarkan ID."""
    db_manager.hapus_sesi(sesi_id)
    return True, "Sesi latihan berhasil dihapus."


def ambil_semua_sesi(filter_instrumen=None, sort_by="tanggal", ascending=False):
    """Mengambil semua sesi latihan dengan opsi filter."""
    return db_manager.get_semua_sesi(filter_instrumen, sort_by, ascending)


def ambil_statistik():
    """Mengambil dan memformat data statistik."""
    raw = db_manager.get_statistik()
    total_jam = raw["total_menit"] // 60
    total_sisa_menit = raw["total_menit"] % 60
    return {
        "total_sesi": raw["total_sesi"],
        "total_menit": raw["total_menit"],
        "total_jam": total_jam,
        "total_sisa_menit": total_sisa_menit,
        "label_durasi": f"{total_jam} jam {total_sisa_menit} menit",
        "per_instrumen": raw["per_instrumen"],
        "per_hari": raw["per_hari"],
    }


def format_durasi(menit):
    """Mengubah menit menjadi format 'Xj Ym'."""
    j = menit // 60
    m = menit % 60
    if j > 0:
        return f"{j}j {m}m"
    return f"{m}m"
