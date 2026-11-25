# Aplikasi Pengolahan Data Inventaris CLI (UTS Pemrograman Dasar)

Aplikasi berbasis *Command Line Interface* (CLI) menggunakan Python untuk membersihkan, memvalidasi, menambahkan, memfilter, dan merekapitulasi data stok inventaris toko dan barang konsinyasi (*consignment*).

## Struktur Proyek
```text
UTS/
├── core_app/               # Package utama pengolahan data
│   ├── __init__.py         # Inisialisasi package dan ekspor fungsi utama
│   ├── file_handler.py     # Modul baca/tambah CSV dan tulis output JSON
│   └── processor.py        # Modul pembersihan duplikat, validasi, filter, dan rekap
├── data/
│   ├── input.csv           # Dataset mentah inventaris (input)
│   └── output.json         # Hasil rekapitulasi dan data bersih (output)
├── main.py                 # Entry point aplikasi CLI dan antarmuka menu
└── README.md               # Dokumentasi penggunaan aplikasi