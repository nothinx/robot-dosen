# robot-dosen

Usulan desain, spesifikasi, dan RAB untuk 3 stasiun PLC dan 3 robot sesuai spesifikasi dari dosen.
Halaman 3D & simulasi: https://nothinx.github.io/robot-dosen/

| Folder | Isi |
|---|---|
| `spesifikasi/` | `*_specs.docx` = asli dari dosen (tidak diubah); `*_specs_usulan.docx` = usulan kami + rincian harga |
| `visual/` | Halaman model 3D, simulasi, dan daftar komponen (PARTS) tiap alat |
| `robot/`, `plc/` | README keputusan desain per alat |
| `tools/` | `isi_spesifikasi.py` membuat docx usulan dari `tools/usul/*.json` + PARTS di `visual/` |

Buat ulang docx usulan setelah mengubah usulan atau harga:

```
pip install python-docx
python tools/isi_spesifikasi.py
```

Status: usulan awal, belum dikonfirmasi dosen. Harga Tokopedia per 6–7 Nov 2026, belum ongkir & PPN.
