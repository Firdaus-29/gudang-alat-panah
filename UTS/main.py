from core_app import (
    baca_inventaris_csv,
    bersihkan_dan_validasi_data,
    filter_barang_by_tipe,
    filter_stok_menipis,
    hitung_rekapitulasi,
    simpan_laporan_json,
    tambah_baris_csv,
    validasi_item_baru,
)

INPUT_PATH = "data/input.csv"
OUTPUT_PATH = "data/output.json"


def tampilkan_daftar_barang(daftar: list, judul: str) -> None:
    """Menampilkan daftar barang inventaris dalam format tabel rapi di terminal."""
    print(f"\n=== {judul} ({len(daftar)} item) ===")
    if not daftar:
        print("Tidak ada data yang sesuai kriteria.")
        return

    print(f"{'ID':<8} | {'Nama Barang':<32} | {'Tipe':<12} | {'Stok':<5} | {'Harga Jual':<13} | {'Status'}")
    print("-" * 88)
    for item in daftar:
        harga_fmt = f"Rp {item['harga_jual']:,}".replace(",", ".")
        print(
            f"{item['id_item']:<8} | "
            f"{item['nama_barang'][:32]:<32} | "
            f"{item['tipe']:<12} | "
            f"{item['stok']:<5} | "
            f"{harga_fmt:<13} | "
            f"{item['status']}"
        )


def jalankan_aplikasi() -> None:
    """Fungsi utama untuk menjalankan alur menu CLI pengolahan data inventaris."""
    print("Memuat data dari", INPUT_PATH, "...")
    data_mentah = baca_inventaris_csv(INPUT_PATH)

    if not data_mentah:
        print("[PERINGATAN] Tidak ada data awal yang terbaca dari CSV.")
        data_bersih, log_error = [], []
    else:
        data_bersih, log_error = bersihkan_dan_validasi_data(data_mentah)
        print(f"Selesai memproses: {len(data_bersih)} data valid, {len(log_error)} baris bermasalah diabaikan.")

    while True:
        print("\n" + "=" * 45)
        print("  SISTEM PENGOLAHAN DATA INVENTARIS CLI")
        print("=" * 45)
        print("1. Tampilkan Semua Inventaris Valid")
        print("2. Filter Berdasarkan Tipe (Stok Toko / Consignment)")
        print("3. Cek Barang Stok Menipis")
        print("4. Lihat Rekapitulasi & Simpan Laporan ke JSON")
        print("5. Lihat Log Error / Data Duplikat yang Ditolak")
        print("6. Tambah Barang Baru")
        print("0. Keluar")

        pilihan = input("Pilih menu (0-6): ").strip()

        if pilihan == "1":
            tampilkan_daftar_barang(data_bersih, "SEMUA INVENTARIS VALID")

        elif pilihan == "2":
            tipe = input("Masukkan tipe barang (Stok Toko / Consignment): ").strip()
            hasil_filter = filter_barang_by_tipe(data_bersih, tipe)
            tampilkan_daftar_barang(hasil_filter, f"FILTER TIPE: {tipe.upper()}")

        elif pilihan == "3":
            batas_input = input("Masukkan batas maksimal stok menipis (default 1): ").strip()
            try:
                batas = int(batas_input) if batas_input else 1
                if batas < 0:
                    print("[ERROR] Batas stok tidak boleh negatif.")
                    continue
                hasil_menipis = filter_stok_menipis(data_bersih, batas)
                tampilkan_daftar_barang(hasil_menipis, f"STOK MENIPIS (<= {batas} UNIT)")
            except ValueError:
                print("[ERROR] Input tidak valid! Harap masukkan angka bulat.")

        elif pilihan == "4":
            rekap = hitung_rekapitulasi(data_bersih)
            print("\n=== REKAPITULASI INVENTARIS ===")
            print(f"Total Jenis Barang Valid : {rekap['total_jenis_barang_valid']} item")
            print(f"Total Unit Tersedia      : {rekap['total_unit_tersedia']} pcs")
            print(f"Jumlah Item SOLD (Stok 0): {rekap['jumlah_item_sold']} item")
            total_rp = f"Rp {rekap['total_nilai_aset_rp']:,}".replace(",", ".")
            print(f"Total Nilai Aset         : {total_rp}")
            print("Rincian Aset per Tipe    :")
            for tipe, nilai in rekap["rincian_aset_per_tipe"].items():
                nilai_rp = f"Rp {nilai:,}".replace(",", ".")
                print(f"  - {tipe}: {nilai_rp}")
            print(f"Kode Pemilik Aktif       : {', '.join(rekap['daftar_pemilik_unik'])}")

            laporan_lengkap = {
                "ringkasan_statistik": rekap,
                "log_validasi_dan_duplikat": log_error,
                "data_inventaris_bersih": data_bersih,
            }
            if simpan_laporan_json(laporan_lengkap, OUTPUT_PATH):
                print(f"\n[SUKSES] Laporan lengkap berhasil disimpan ke '{OUTPUT_PATH}'.")

        elif pilihan == "5":
            print("\n=== LOG DATA DUPLIKAT & TIDAK VALID ===")
            if not log_error:
                print("Tidak ditemukan error pada data input.")
            else:
                for catatan in log_error:
                    print("-", catatan)

        elif pilihan == "6":
            print("\n=== TAMBAH BARANG INVENTARIS BARU ===")
            id_baru = input("ID Item (contoh: ITM009)          : ")
            nama_baru = input("Nama Barang                       : ")
            print("Pilih Tipe: [1] Stok Toko  [2] Consignment")
            pilih_tipe = input("Tipe (1/2)                        : ").strip()
            tipe_baru = "Stok Toko" if pilih_tipe == "1" else ("Consignment" if pilih_tipe == "2" else "")

            size_baru = input("Size (kosongkan jika '-')         : ")
            warna_baru = input("Warna (kosongkan jika '-')        : ")
            stok_baru = input("Jumlah Stok (angka)               : ")
            harga_baru = input("Harga Jual dalam Rp (angka)       : ")
            pemilik_baru = input("Kode Pemilik (default XMael)      : ")

            calon_item = {
                "id_item": id_baru,
                "nama_barang": nama_baru,
                "tipe": tipe_baru,
                "size": size_baru,
                "warna": warna_baru,
                "stok": stok_baru,
                "harga_jual": harga_baru,
                "kode_pemilik": pemilik_baru,
            }

            sukses_validasi, hasil = validasi_item_baru(data_bersih, calon_item)
            if not sukses_validasi:
                print(f"[ERROR] Gagal menambahkan barang: {hasil}")
            else:
                if tambah_baris_csv(hasil, INPUT_PATH):
                    data_bersih.append(hasil)
                    print(f"[SUKSES] Barang '{hasil['nama_barang']}' ({hasil['id_item']}) berhasil ditambahkan & disimpan ke CSV!")

        elif pilihan == "0":
            print("Keluar dari program. Terima kasih!")
            break

        else:
            print("[ERROR] Pilihan menu tidak tersedia. Silakan pilih angka 0 sampai 6.")


if __name__ == "__main__":
    jalankan_aplikasi()