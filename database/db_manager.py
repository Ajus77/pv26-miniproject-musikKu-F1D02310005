"""
database/db_manager.py
Modul untuk mengelola koneksi dan operasi database SQLite.
Separation of Concerns: Hanya berisi logika database.
"""

import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musikku.db")


def get_connection():
    """Membuat dan mengembalikan koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesi_latihan (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal     TEXT    NOT NULL,
            instrumen   TEXT    NOT NULL,
            materi      TEXT    NOT NULL,
            durasi      INTEGER NOT NULL,
            mood        TEXT    NOT NULL,
            catatan     TEXT,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    conn.close()


def tambah_sesi(tanggal, instrumen, materi, durasi, mood, catatan):
    """Menambahkan sesi latihan baru ke database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sesi_latihan (tanggal, instrumen, materi, durasi, mood, catatan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tanggal, instrumen, materi, durasi, mood, catatan))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_semua_sesi(filter_instrumen=None, sort_by="tanggal", ascending=False):
    """Mengambil semua sesi latihan dari database dengan opsi filter dan sort."""
    conn = get_connection()
    cursor = conn.cursor()

    order = "ASC" if ascending else "DESC"
    valid_sort = {"tanggal", "instrumen", "durasi", "mood"}
    if sort_by not in valid_sort:
        sort_by = "tanggal"

    if filter_instrumen and filter_instrumen != "Semua":
        cursor.execute(
            f"SELECT * FROM sesi_latihan WHERE instrumen = ? ORDER BY {sort_by} {order}",
            (filter_instrumen,)
        )
    else:
        cursor.execute(f"SELECT * FROM sesi_latihan ORDER BY {sort_by} {order}")

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_sesi_by_id(sesi_id):
    """Mengambil satu sesi latihan berdasarkan ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sesi_latihan WHERE id = ?", (sesi_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_sesi(sesi_id, tanggal, instrumen, materi, durasi, mood, catatan):
    """Memperbarui data sesi latihan yang sudah ada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sesi_latihan
        SET tanggal=?, instrumen=?, materi=?, durasi=?, mood=?, catatan=?
        WHERE id=?
    """, (tanggal, instrumen, materi, durasi, mood, catatan, sesi_id))
    conn.commit()
    conn.close()


def hapus_sesi(sesi_id):
    """Menghapus sesi latihan berdasarkan ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sesi_latihan WHERE id = ?", (sesi_id,))
    conn.commit()
    conn.close()


def get_statistik():
    """Mengambil data statistik latihan dari database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_sesi, SUM(durasi) as total_menit FROM sesi_latihan")
    stat = cursor.fetchone()

    cursor.execute("""
        SELECT instrumen, COUNT(*) as jumlah, SUM(durasi) as total_menit
        FROM sesi_latihan
        GROUP BY instrumen
        ORDER BY total_menit DESC
    """)
    per_instrumen = cursor.fetchall()

    cursor.execute("""
        SELECT tanggal, SUM(durasi) as total_menit
        FROM sesi_latihan
        GROUP BY tanggal
        ORDER BY tanggal DESC
        LIMIT 7
    """)
    per_hari = cursor.fetchall()

    conn.close()
    return {
        "total_sesi": stat["total_sesi"] or 0,
        "total_menit": stat["total_menit"] or 0,
        "per_instrumen": [dict(r) for r in per_instrumen],
        "per_hari": [dict(r) for r in per_hari],
    }
