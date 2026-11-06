# P1 — Konveyor pengepakan

Spesifikasi asli (`spesifikasi/PLC_specs.docx`):
- Memiliki 2 sub-konveyor yaitu main infeed conveyor dan packing conveyor
- Dimensi main infeed conveyor (p × l) ± 1500 mm × 100 mm
- Dimensi packing conveyor (p × l) ± 2000 mm × 600 mm
- "Diameter kapasitas" ± 20 kg untuk tiap konveyor (salah ketik, maksudnya kapasitas beban)
- Sensor fotoelektrik, proksimitas, load cell, dan enkoder konveyor
- Konstruksi stainless steel
- Motor penggerak 24 VDC dengan girboks
- Katup pneumatik sebagai aktuator
- Panel kontrol elektronik

## Keputusan
Usulan + RAB Tokopedia (dicek 7 Nov 2026, total **±Rp30,91 jt** belum ongkir, 50 baris) ada di
`visual/p1-pengepakan.html` (model 3D + simulasi siklus PLC dengan tabel I/O hidup) dan di docx lewat
`tools/usul/p1-pengepakan.json`. Status: **usulan awal, belum dikunci**.

Keputusan bersama P1–P3: PLC Siemens S7-1200 CPU 1214C AC/DC/RLY satu per stasiun, panel box besi + MCB + PSU Meanwell,
tombol Start/Stop/Reset, selektor Auto/Manual, E-stop, pilot lamp, semua aktuator & sensor 24 VDC.

- **Tata letak**: infeed sejajar packing di sisi +z, belt infeed 1050 mm dari lantai (di atas bibir kardus 250 mm),
  belt packing 750 mm. Produk ditahan palang di ujung infeed tepat di atas stasiun isi; silinder mendorongnya menyamping
  lewat talang ke kardus 40 × 30 × 25 cm. Kardus menempel pemandu samping supaya proksimitas bisa melihatnya.
- **Urutan proses (mode Auto)**:
  1. Start → bila PX1 melihat kardus di stasiun isi langsung mengisi, bila tidak packing maju satu pitch.
  2. Kardus diam ±0,5 s → PLC mencatat tara dari load cell.
  3. PE1 melihat produk di palang dan silinder di belakang (B0) → Y1 aktif, silinder maju; B1 → hitungan +1, Y1 mati;
     B0 → tunggu 0,6 s lalu timbang (berat bersih = AI − tara).
  4. Ulangi sampai jumlah produk per kotak (parameter, bawaan 10). Berat kotak dibandingkan jumlah × berat nominal.
  5. Kotak maju **500 mm diukur enkoder** (HSC1, target absolut supaya galat tidak menumpuk; motor dimatikan
     ±6 mm lebih awal untuk kompensasi luncur). Kardus penuh tiba di posisi ambil (PE2), kardus kosong berikutnya di stasiun isi.
  6. Pitch hanya boleh jalan bila PE2 kosong (kardus penuh sudah diambil). 3 pitch tanpa kardus → lampu kuning, tunggu Start.
  - Infeed jalan terus selama siklus (produk antre di palang, belt meluncur di bawahnya); berhenti bila produk sudah menunggu
    dan packing sedang pitch. Silinder tidak sampai B1/B0 dalam 2 s, atau enkoder diam 6 s saat pitch → gangguan (lampu merah, Reset).
  - Manual: tahan Start = jalankan packing, tahan Reset = jalankan infeed, tahan Dorong = silinder maju.
- **Daya motor** (packing, terberat): F = μ·(m beban + m belt atas)·g·1,15 = 0,33 × (20 + 2,9) × 9,81 × 1,15 ≈ 85 N;
  pulley Ø76,2 mm → 3,2 N·m (lepas diam μ 0,45 → 3,9 N·m); pada 0,16 m/s = 13,6 W keluaran.
  Motor **Houle 5DC60W 24 V** (2000 rpm, 3,5 A) + gearhead 5GU 1:50 (40 rpm, 0,16 m/s) untuk packing, 1:36 (55 rpm,
  8,55 N·m, 0,22 m/s) untuk infeed. 60 W × 0,7 efisiensi gear = 42 W, cadangan ±3×. Set sudah termasuk pengatur kecepatan DC.
  Relay PLC hanya 2 A → relay perantara Omron LY2N 10 A memutus catu 24 V ke pengatur kecepatan.
- **PSU**: beban terburuk 2 × 3,5 A + katup 0,1 A + sensor/lampu/transmitter ±0,5 A = 7,6 A → **Meanwell NDR-240-24 (10 A)**,
  bukan EDR-120-24 (5 A). PLC AC/DC/RLY dicatu 220 VAC langsung.
- **Enkoder**: Omron E6B2-CWZ5B 1000 P/R PNP di as pulley ekor packing (tidak digerakkan motor). HSC1 A/B x4 = 4000 cacah per
  putaran = 16.709 cacah per meter (0,06 mm/cacah); pitch 500 mm = 8.355 cacah. Frekuensi ±670 Hz, batas HSC 100 kHz.
- **Load cell**: Zemic L6E single point 50 kg di bawah pelat timbang 420 × 420 mm yang sebidang dengan alas luncur; belt lewat
  di atasnya. Transmitter WXD-D70 0–10 V ke AI0 %IW64 (0–27648 = 0–50 kg). Resolusi AI 10 bit ±50 g, akurasi transmitter
  0,2% FS ±0,1 kg. Cukup untuk cek isi kotak (produk ±1 kg), bukan timbangan dagang.
- **Proksimitas**: kapasitif LJC18A3 karena kardus bukan logam (induktif tidak bisa). Jarak 10 mm → kardus wajib menempel pemandu.
- **Pneumatik**: kompresor oilless JLD 30 L 1100 W **dibeli sekali di P1 dan dipakai bersama P2** (P2 tidak membeli kompresor).
  FRL AFC-2000 disetel 4 bar; katup 5/2 Airtac 4V210-08 24 VDC solenoid tunggal (daya hilang = silinder mundur);
  silinder SC 32 × 200 bermagnet + 2 reed switch CS1-F, speed controller meter-out. Konsumsi ±2,3 NL per dorongan pada 6 bar.
- **Konstruksi**: dirakit sendiri dari bahan SS304 (hollow 40 × 40 × 1,5, plat 1,5 mm, pipa 3" untuk pulley, as Ø20) + bearing
  UCP204 (kepala) / UCT204 take-up (ekor) + belt PVC putih food grade 2 mm. Bubut pulley dan las argon dari listing jasa
  (**estimasi**: bubut 240 × Rp5.000 ≈ Rp1,2 jt, las 8 hari × Rp270.000). Pembanding konveyor jadi: Karang Mutu Abadi SS
  148 × 20 cm Rp7 jt/unit; convayer.eng mulai Rp10,5 jt/unit (packing 600 mm pasti lebih mahal).
- **HMI** tidak diminta → tidak dibeli. Opsi: panel sentuh Siemens KTP400 untuk parameter (jumlah per kotak, pitch, kalibrasi).
  Alternatif PLC murah: Outseal (lokal, Arduino-based) memangkas ±Rp7 jt, tetapi tanpa HSC 100 kHz dan AI 0–10 V bawaan
  setara, dan bukan standar praktikum TIA Portal.

## Daftar I/O (CPU 1214C)

| Alamat | Tag | Fungsi |
|---|---|---|
| %I0.0 | ENC_A | Enkoder fase A (HSC1) |
| %I0.1 | ENC_B | Enkoder fase B (HSC1) |
| %I0.2 | PE1 | Fotoelektrik: produk di palang ujung infeed |
| %I0.3 | PX1 | Proksimitas kapasitif: kardus di stasiun isi |
| %I0.4 | PE2 | Fotoelektrik: kardus penuh di posisi ambil (x = +500 mm) |
| %I0.5 | B0 | Reed switch silinder di belakang |
| %I0.6 | B1 | Reed switch silinder di depan |
| %I0.7 | S1 | Start (NO) |
| %I1.0 | S2 | Stop (NC) |
| %I1.1 | S3 | Reset (NO) |
| %I1.2 | S4 | Dorong manual (NO) |
| %I1.3 | S5 | Selektor Auto (1) / Manual (0) |
| %I1.4 | ES | +24 V setelah kontak NC E-stop (1 = daya aktuator ada) |
| %I1.5 | – | Cadangan |
| %Q0.0 | K1 | Relay motor infeed (grup 1L) |
| %Q0.1 | K2 | Relay motor packing (grup 1L) |
| %Q0.2 | Y1 | Katup 5/2 silinder pendorong (grup 1L) |
| %Q0.3–%Q0.4 | – | Cadangan (grup 1L) |
| %Q0.5 | H1 | Lampu hijau: jalan otomatis (grup 2L) |
| %Q0.6 | H2 | Lampu kuning: menunggu / manual |
| %Q0.7 | H3 | Lampu merah: gangguan / E-stop |
| %Q1.0–%Q1.1 | – | Cadangan (grup 2L) |
| %IW64 (AI0) | WT1 | Load cell via transmitter 0–10 V (0–50 kg) |
| %IW66 (AI1) | – | Cadangan (mis. sensor tekanan udara) |

Terpakai 13 DI, 6 DO, 1 AI → sisa untuk latihan mahasiswa.

**Wiring 1M (sink/source)**: semua 14 DI 1214C memakai satu common **1M**. Semua sensor dipilih **PNP** (sourcing), maka
**1M disambung ke 0 V (M)** dan sensor mengeluarkan +24 V saat aktif. Tombol, selektor, reed switch 2 kabel: satu sisi ke +24 V,
sisi lain ke masukan. Konsekuensi: P2 dan P3 juga harus PNP (atau semuanya NPN dengan 1M ke +24 V); jangan dicampur dalam satu
grup. Keluaran relay: common **1L** dicatu +24 V **lewat kontak NC E-stop** (motor dan katup mati secara kabel walau program
keliru), **2L** dicatu +24 V langsung supaya lampu merah tetap bisa menyala saat E-stop. Kabel lapangan mendarat di terminal
UK-3N, bukan langsung ke PLC. Rangka konveyor dan box panel dibumikan.

## Belum pasti
- Satuan harga jasa las (per hari? per titik?) dan bubut: angka pasti dari penawaran bengkel. Bila memesan konveyor jadi,
  RAB konstruksi (±Rp12,7 jt bahan + jasa) diganti penawaran pabrikan.
- Penimbangan di atas belt: tarikan belt ikut terbaca. Model menganggap tara saat belt diam menghapus offset; perlu uji nyata.
- Gearhead 5GU 1:50: torsi izin dari lembar data Houle (listing terpotong di 1:50); 1:36 = 8,55 N·m sudah cukup.
- Pengatur kecepatan Houle: apakah aman diputus-sambung catunya oleh relay atau perlu masukan run/stop sendiri.
- Encoder E6B2-CWZ5B di listing PLC Centre: pilih varian 1000 P/R saat memesan.
- Belt 650 mm dipotong 600 atau dipesan custom; sambungan endless dari toko belt.
- Simulasi: model kinematik sederhana (luncur belt τ 40 ms, gesek μ 0,33), angka untuk gambaran, bukan hasil uji.
