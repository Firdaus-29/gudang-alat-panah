import csv
import json
import os

FIELDNAMES_CSV = [
    "id_item",
    "nama_barang",
    "tipe",
    "size",
    "warna",
    "stok",
    "kode_pemilik",
    "harga_jual",
    "status",
]


def baca_inventaris_csv(file_path: str) -> list:
    """Membaca data inventaris dari file CSV menjadi list of dictionary.

    Args:
        file_path (str): Lokasi path file CSV yang akan dibaca.

    Returns:
        list: Kumpulan baris data dalam bentuk dictionary, atau list kosong jika
        gagal.
    """
    data_mentah = []
    try:
        with open(file_path, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for baris in reader:
                data_mentah.append(dict(baris))
        return data_mentah
    except FileNotFoundError:
        print(f"[ERROR] File tidak ditemukan di lokasi: {file_path}")
        return []
    except Exception as err:
        print(f"[ERROR] Gagal membaca file CSV: {err}")
        return []


def simpan_laporan_json(data: dict, file_path: str) -> bool:
    """Menyimpan hasil analisis dan rekapitulasi inventaris ke dalam file JSON.

    Args:
        data (dict): Struktur data hasil rekapitulasi yang akan disimpan.
        file_path (str): Lokasi tujuan penyimpanan file JSON.

    Returns:
        bool: True jika penyimpanan berhasil, False jika terjadi error.
    """
    try:
        folder = os.path.dirname(file_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except (OSError, TypeError) as err:
        print(f"[ERROR] Gagal menyimpan laporan ke JSON: {err}")
        return False


def tambah_baris_csv(item_baru: dict, file_path: str) -> bool:
    """Menambahkan satu baris data barang baru ke akhir file CSV.

    Args:
        item_baru (dict): Data barang yang sudah lolos validasi.
        file_path (str): Lokasi path file CSV tujuan.

    Returns:
        bool: True jika berhasil disimpan ke CSV, False jika gagal.
    """
    try:
        file_ada = os.path.exists(file_path) and os.path.getsize(file_path) > 0
        with open(file_path, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES_CSV)
            if not file_ada:
                writer.writeheader()
            writer.writerow(item_baru)
        return True
    except OSError as err:
        print(f"[ERROR] Gagal menambahkan data ke CSV: {err}")
        return False