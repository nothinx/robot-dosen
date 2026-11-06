# P2 — Konveyor sortir

Spesifikasi asli (`spesifikasi/PLC_specs.docx`):
- 1 konveyor, dimensi (p × l) ± 3000 mm × 200 mm
- Dua bin: bin normal dan reject
- Kapasitas konveyor ± 20 kg
- Berat ± 6 kg
- Sensor fotoelektrik, warna, kamera, dan enkoder konveyor
- Konstruksi stainless steel
- Motor penggerak 24 VDC dengan girboks
- Katup pneumatik sebagai aktuator
- Panel kontrol elektronik

## Keputusan
Usulan + RAB Tokopedia (dicek 7 Nov 2026, total **±Rp25,86 jt** belum ongkir) ada di docx dan di
`visual/p2-sortir.html` (model 3D + simulasi PLC hidup). Status: **usulan awal, belum dikunci**.
Subtotal: panel kontrol ±Rp9,40 jt (PLC Rp7,65 jt), konveyor & penggerak ±Rp7,92 jt, sensor & vision ±Rp7,45 jt
(paket Pi + kamera ±Rp5,54 jt), pneumatik & bin ±Rp1,08 jt.

### Keputusan bersama P1, P2, P3
- PLC Siemens S7-1200 CPU 1214C AC/DC/RLY (6ES7214-1BG40-0XB0), satu per stasiun: 14 DI 24 VDC, 10 DO relay,
  2 AI 0–10 V, HSC untuk enkoder, Ethernet/TIA Portal. Alternatif murah: **Outseal** (PLC lokal berbasis Arduino,
  diprogram ladder, harga jauh di bawah S7; belum dicek di Tokopedia), cukup untuk praktikum logika dasar, tetapi tanpa HSC kelas S7 dan tanpa TIA Portal.
- Panel per stasiun: box, MCB, PSU Meanwell 24 V, tombol Start/Stop/Reset, selector Auto/Manual, E-stop, pilot lamp,
  terminal block, rel DIN. HMI tidak diminta → opsi (mis. KTP400 Basic) di luar RAB.
- **Kompresor dibeli di P1 dan dipakai bersama**; P2 hanya membawa filter regulator, katup, silinder, selang, fitting.
- Semua sensor & aktuator 24 VDC. Sensor NPN; common DI (1M) disambung ke +24 V (S7-1200 menerima sink/source).

### Konstruksi & penggerak
- Belt PVC putih food grade 200 × 2 mm, panjang sumbu pulley 3000 mm, alas luncur pelat stainless 1,2 mm.
  Rangka hollow SS304 40 × 40 × 1,2, tinggi permukaan belt 800 mm, 6 kaki penyetel M10. Dirakit dari komponen +
  jasa las TIG (konveyor stainless jadi 3 m di Tokopedia tidak ada; frame jadi 1 m saja Rp3 jt).
- Pulley Ø60 as 15 mm (kepala knurling) di bearing UCFL 202; pulley ekor di dudukan beralur untuk menegangkan belt.
- **Motor**: Houle 5DC60W 24 V + girboks 5GU36K + pengendali kecepatan (satu set). Hitungan untuk beban 20 kg:
  F = μ·(20 + 3 kg belt)·g·1,3 = 0,35 × 23 × 9,81 × 1,3 ≈ 103 N; torsi di pulley Ø60 = 103 × 0,03 ≈ **3,1 N·m**;
  daya keluaran di 0,25 m/s ≈ 26 W, masukan ≈ 40 W (girboks 65%). Set 60 W/1:36 → ±83 rpm (belt maks ±0,26 m/s),
  torsi ±5,5 N·m (estimasi dari 60 W di ±3000 rpm), cadangan 1,8×. Kopling jaw L-075 ke as pulley.
- Kecepatan diatur kenop pengendali motor di pintu panel, bukan oleh PLC: CPU AC/DC/RLY tidak punya keluaran analog.
  Ini aman karena pelacakan memakai enkoder, bukan waktu. PLC hanya menyalakan motor (Q0.0 → relay K1).
  Bila kecepatan harus diatur program: signal board SB 1232 AQ (opsi).

### Sensor, kamera, pelacakan
- **PE1** E3F-DS30C4 di 700 mm dari ujung masuk memulai pelacakan; **sensor warna** OETAI GDS-3011 di 850 mm;
  **kamera** di 1100 mm di bawah kerudung stainless dengan LED strip COB; **silinder reject** di 2000 mm;
  **PE2** di 2800 mm menghitung produk masuk bin normal. Bin normal di ujung, bin reject di samping (corong).
- Sensor warna jarak baca 10 ± 2 mm, titik cahaya 1 mm → dipasang di jendela rel pemandu dan membaca **sisi** produk;
  rel pemandu menjaga jarak. Diajari warna produk benar, keluaran 1 = warna sesuai.
- **Kamera tidak bisa diolah PLC** → Raspberry Pi 5 4 GB + Camera Module 3 (OpenCV: goresan, label hilang).
  Paket ±Rp5,5 jt. Sensor vision mandiri di Tokopedia: Omron FQ2 Rp30 jt, Hikrobot smart camera Rp129,8 jt
  → tidak wajar untuk alat praktikum. Pi juga bisa dipakai mahasiswa belajar olah citra.
- Pi ↔ PLC lewat **I/O digital**, bukan Modbus TCP: PLC memicu Pi (Q0.2 → optocoupler 24 V→3,3 V), Pi menjawab
  "hasil siap" (I0.4) + "OK" (I0.5) lewat modul relay 2 kanal (kontak kering, isolasi penuh). Alasan: deterministik,
  terlihat langsung di tabel I/O, tidak perlu switch Ethernet (1214C hanya punya 1 port) dan blok MB_SERVER.
  Modbus TCP = opsi lanjutan bila ingin mengirim jenis cacat/statistik (tambah switch ±Rp150 rb).
- **Enkoder** Omron E6B2-CWZ6C 600 P/R di as pulley ekor (tidak digerakkan motor → tidak ikut slip penggerak),
  HSC1 mode A/B ×4: 2400 hitungan/putaran, π × 60 / 2400 ≈ **0,079 mm/hitungan**; frekuensi maks ±830 Hz.
- **Pelacakan (shift register/FIFO)** di program PLC:
  1. Tepi naik PE1 → masukkan {hitungan HSC saat itu} ke antrian (array 16 elemen di DB).
  2. Tiap scan: jarak = (HSC − c0) × 0,079 mm. Saat tengah produk di sensor warna (+190 mm) → simpan I0.3.
  3. Di kamera (+440 mm) → pulsa Q0.2 50 ms; jawaban Pi pertama dicocokkan ke produk tertua yang menunggu.
     Pi tidak menjawab dalam 500 ms → dianggap NG (gagal-aman, produk dibuang, bukan diloloskan).
  4. NG dan jarak ≥ 1340 mm − lead → Q0.1 sampai reed "maju"; lead = kecepatan terukur × 0,18 s
     (jeda katup 30 ms + pelat menempuh 75 mm ke produk), ±27 mm di 0,15 m/s. Tembakan berikut menunggu reed "mundur".
  5. Elemen dihapus setelah melewati ujung belt. Stop/E-stop tidak menghapus antrian: belt diam, HSC ikut diam.
  Hasil simulasi 5 menit (30% produk menyimpang): enkoder 0 salah sortir di 0,05; 0,15; 0,25 m/s.
  Pembanding timer tetap (dikalibrasi 0,15 m/s): 1 / 22 / 18 salah di 0,15 / 0,25 / 0,08 m/s.
- Silinder Airtac MAL 20 × 200 bermagnet + 2 reed switch CS1-U: gaya ±157 N di 5 bar, cukup untuk produk
  sampai 6 kg (gesek + percepatan ±45 N). Katup 4V210-08 24 VDC 5/2 kembali pegas.

### Daftar I/O (S7-1214C AC/DC/RLY)
| Alamat | Sinyal | | Alamat | Sinyal |
|---|---|---|---|---|
| %I0.0 / %I0.1 | Enkoder A / B (HSC1, %ID1000) | | %Q0.0 | Motor jalan (relay K1 → pengendali motor) |
| %I0.2 | PE1 fotoelektrik inspeksi | | %Q0.1 | Katup 5/2 silinder reject |
| %I0.3 | Sensor warna: sesuai | | %Q0.2 | Pemicu kamera ke Pi (optocoupler) |
| %I0.4 | Pi: hasil siap (strobe) | | %Q0.3 | Lampu hijau: jalan |
| %I0.5 | Pi: produk OK | | %Q0.4 | Lampu kuning: siaga |
| %I0.6 | E-stop (kontak relay K0, NC) | | %Q0.5 | Lampu merah: gangguan |
| %I0.7 | PE2 fotoelektrik ujung | | %Q0.6 | LED penerang kamera |
| %I1.0 / %I1.1 | Reed silinder mundur / maju | | %Q0.7, %Q1.0, %Q1.1 | Cadangan |
| %I1.2 / %I1.3 | Start (NO) / Stop (NC) | | %IW64 | AI0 cadangan (opsi sensor tekanan 0–10 V) |
| %I1.4 / %I1.5 | Reset (NO) / Auto-Manual | | %IW66 | AI1 cadangan |

Semua 14 DI terpakai. Manual: konveyor jalan selama Start ditekan, Reset menembak silinder sekali (uji).

### Panel & keselamatan
- E-stop 1NC memutus koil relay K0; kontak K0 memberi 24 V ke pengendali motor dan katup → berhenti tanpa menunggu
  PLC, silinder mundur oleh pegas. Kontak kedua K0 dibaca %I0.6. Reset diperlukan setelah E-stop dilepas.
- Catu Meanwell NDR-240-24 (10 A), bukan EDR-120-24: beban kontinu ±4,5 A (motor ±3,2 A, Pi ±0,4 A, LED, katup,
  sensor) dan arus start motor ±2×.
- Pi, buck 24→5 V, optocoupler, relay di kotak ABS IP65 di atas kerudung kamera (kabel kamera Pi 5 hanya 20 cm).
- Q0.2 berkedip sekali per produk (±1200×/jam di 20 produk/menit). Umur listrik relay 100 rb kali di beban penuh;
  beban optocoupler hanya ±10 mA sehingga jauh lebih awet, tetapi untuk pemakaian berat pasang signal board
  SB 1222 (keluaran transistor) atau pakai CPU DC/DC/DC.

### Berat
- "Berat ± 6 kg" tidak mungkin untuk konveyor stainless 3 m: hollow ±20 kg, pelat ±11 kg, pulley ±4 kg, belt ±3 kg,
  motor ±3,5 kg, bearing & lain-lain ±5 kg → **±47 kg** (estimasi), panel + tiang ±8 kg terpisah.
- Tafsiran kami: 6 kg = **berat maksimum satu produk**. Silinder Ø20 sanggup (lihat atas); kapasitas 20 kg = total
  muatan di belt sekaligus (mis. 10 produk × 2 kg). Bila maksudnya 60 kg (salah ketik), usulan ini sudah sesuai.

## Belum pasti / dikonfirmasi
- Harga fabrikasi: plat (harga tertera varian 201; 304 lebih mahal), jasa las (satuan toko tidak jelas, dianggap
  4 hari kerja), pulley custom (dipesan ukuran), tekuk pelat → minta penawaran bengkel. Bisa ±Rp1–3 jt.
- Varian motor 24 V/5GU36K: harga tertera untuk varian 12 V/3K; rpm & torsi dari kelas motor, cek lembar data.
- GDS-3011 adalah sensor *color mark* (titik 1 mm): cocok untuk produk seragam; produk beragam tinggi/tekstur
  butuh sensor warna jarak jauh (lebih mahal) atau warna dibaca kamera saja.
- Sambung belt: endless (sambung panas) dari toko lebih baik daripada clipper di pulley Ø60.
- Band pemasang reed switch untuk MAL 20, panjang selang dari kompresor P1 (tergantung tata letak lab).
- Ongkir belum termasuk; komponen stainless berat/panjang (hollow 6 m) ongkirnya besar.
