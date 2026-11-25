def bersihkan_dan_validasi_data(data_mentah: list) -> tuple[list, list]:
    """Membersihkan data duplikat memakai set dan memvalidasi tipe angka stok/harga.

    Args:
        data_mentah (list): Daftar dictionary mentah hasil pembacaan CSV.

    Returns:
        tuple[list, list]: Tuple berisi (data_bersih, log_error).
    """
    seen_ids = set()
    data_bersih = []
    log_error = []

    for nomor_baris, baris in enumerate(data_mentah, start=2):
        id_item = baris.get("id_item", "").strip().upper()

        if not id_item or id_item in seen_ids:
            log_error.append(
                f"Baris {nomor_baris}: ID '{id_item}' kosong atau duplikat (dilewati)."
            )
            continue

        try:
            stok = int(baris.get("stok", 0))
            harga = int(baris.get("harga_jual", 0))
        except ValueError:
            log_error.append(
                f"Baris {nomor_baris} ({id_item}): Format stok/harga bukan angka valid."
            )
            continue

        if stok < 0 or harga < 0:
            log_error.append(
                f"Baris {nomor_baris} ({id_item}): Stok ({stok}) atau harga ({harga}) negatif."
            )
            continue

        seen_ids.add(id_item)
        item_valid = {
            "id_item": id_item,
            "nama_barang": baris.get("nama_barang", "").strip(),
            "tipe": baris.get("tipe", "").strip(),
            "size": baris.get("size", "-").strip(),
            "warna": baris.get("warna", "-").strip(),
            "stok": stok,
            "harga_jual": harga,
            "kode_pemilik": baris.get("kode_pemilik", "").strip(),
            "status": "SOLD" if stok == 0 else baris.get("status", "Tersedia").strip(),
        }
        data_bersih.append(item_valid)

    return data_bersih, log_error


def validasi_item_baru(data_bersih: list, input_mentah: dict) -> tuple[bool, dict | str]:
    """Memvalidasi data barang baru sebelum ditambahkan ke inventaris.

    Args:
        data_bersih (list): Daftar item valid yang sudah ada saat ini.
        input_mentah (dict): Data mentah dari input pengguna di terminal.

    Returns:
        tuple[bool, dict | str]: (True, item_valid) jika valid, atau (False,
        pesan_error) jika tidak valid.
    """
    seen_ids = {item["id_item"].upper() for item in data_bersih}
    id_item = input_mentah.get("id_item", "").strip().upper()
    nama_barang = input_mentah.get("nama_barang", "").strip()
    tipe = input_mentah.get("tipe", "").strip()

    if not id_item:
        return False, "ID item tidak boleh kosong."
    if id_item in seen_ids:
        return False, f"ID '{id_item}' sudah terdaftar di inventaris (duplikat)."
    if not nama_barang:
        return False, "Nama barang tidak boleh kosong."
    if tipe not in ("Stok Toko", "Consignment"):
        return False, "Tipe barang harus 'Stok Toko' atau 'Consignment'."

    try:
        stok = int(input_mentah.get("stok", ""))
        harga = int(input_mentah.get("harga_jual", ""))
    except ValueError:
        return False, "Stok dan harga jual harus berupa angka bulat."

    if stok < 0 or harga < 0:
        return False, "Stok dan harga jual tidak boleh bernilai negatif."

    kode_pemilik = input_mentah.get("kode_pemilik", "").strip()
    if not kode_pemilik:
        kode_pemilik = "XMael" if tipe == "Stok Toko" else "UNKNOWN"

    item_valid = {
        "id_item": id_item,
        "nama_barang": nama_barang,
        "tipe": tipe,
        "size": input_mentah.get("size", "").strip() or "-",
        "warna": input_mentah.get("warna", "").strip() or "-",
        "stok": stok,
        "kode_pemilik": kode_pemilik,
        "harga_jual": harga,
        "status": "SOLD" if stok == 0 else "Tersedia",
    }
    return True, item_valid


def filter_barang_by_tipe(data_bersih: list, tipe_dicari: str) -> list:
    """Memfilter daftar inventaris berdasarkan tipe (Stok Toko / Consignment) menggunakan list comprehension."""
    return [
        item for item in data_bersih
        if item["tipe"].lower() == tipe_dicari.strip().lower()
    ]


def filter_stok_menipis(data_bersih: list, batas_maksimal: int = 1) -> list:
    """Mengambil daftar barang yang masih tersedia tetapi stoknya menipis (<= batas_maksimal)."""
    return [
        item for item in data_bersih
        if 0 < item["stok"] <= batas_maksimal
    ]


def hitung_rekapitulasi(data_bersih: list) -> dict:
    """Menghitung ringkasan statistik inventaris, nilai aset per tipe, dan daftar pemilik unik."""
    pemilik_unik = sorted({item["kode_pemilik"] for item in data_bersih if item["kode_pemilik"]})
    tipe_unik = {item["tipe"] for item in data_bersih}

    nilai_aset_per_tipe = {
        tipe: sum(item["stok"] * item["harga_jual"] for item in data_bersih if item["tipe"] == tipe)
        for tipe in tipe_unik
    }

    total_unit = sum(item["stok"] for item in data_bersih)
    total_nilai_aset = sum(nilai_aset_per_tipe.values())
    jumlah_sold = sum(1 for item in data_bersih if item["stok"] == 0)

    return {
        "total_jenis_barang_valid": len(data_bersih),
        "total_unit_tersedia": total_unit,
        "jumlah_item_sold": jumlah_sold,
        "total_nilai_aset_rp": total_nilai_aset,
        "rincian_aset_per_tipe": nilai_aset_per_tipe,
        "daftar_pemilik_unik": pemilik_unik,
    }