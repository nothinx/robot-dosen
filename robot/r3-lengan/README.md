# R3 — Lengan robot

Spesifikasi asli (`spesifikasi/robotic_arm_specs.docx`):
- 6-DOF, jangkauan ± 1000 mm
- Rangka aluminium / logam campuran
- End-effector gripper atau tool lain
- Servo digital ber-enkoder (kontrol kecepatan, posisi, atau torsi)
- Pengendali Arduino Mega
- Kekakuan & backlash < 1°
- Sensor: enkoder, kamera stereoskopik, proksimitas
- Catu daya 220 VAC

## Keputusan
Usulan + RAB Tokopedia (dicek 7 Nov 2026, total ±Rp25,11 jt belum ongkir) ada di `tools/usul/r3-lengan.json` dan
`visual/r3-lengan.html` (model 3D, IK klik-target, demo ambil-taruh, torsi tiap sendi vs rating). Status: **usulan awal, belum dikunci**.

- **Beban 0,5 kg di ujung pada jangkauan penuh** (dosen tidak menyebut; alat peraga/praktikum ambil-taruh). Benda uji: kubus baja 40 mm ≈ 0,5 kg.
- **Geometri**: sumbu bahu 490 mm di atas meja, lengan atas 450 mm, lengan bawah 380 mm, pergelangan (J5) ke ujung gripper 170 mm
  → jangkauan horizontal 1000 mm dari sumbu J1. Lengan atas offset 60 mm ke samping supaya J3 tidak menabrak lengan bawah.
- **Pengendali**: STM32 Black Pill WeAct F411CEU6 (sama dengan R1) sebagai pengendali sendi waktu-nyata; IK & olah kamera stereo di PC lab
  lewat USB. Arduino Mega ditolak (8-bit, tanpa FPU). Pulsa langkah ke 3 driver servo AC lewat optocoupler 6N137; bus RS485 Modbus ke 3 MKS.
- **J1–J3: servo AC 220 V + driver (17-bit, mode posisi/kecepatan/torsi) + gearbox planetary presisi.**
  J2 (bahu) dan J3 (siku) memakai motor **ber-rem** supaya lengan tidak jatuh saat daya putus/E-stop.
- **J4–J6: NEMA17 17HS8401 + gearbox Cloudray FLE42 1:10 + driver closed-loop MKS SERVO42D RS485.**
- **Gripper**: capit aluminium + servo DS3225 25 kg·cm (gaya perlu 12 N, tersedia ±40 N). Proksimitas: ToF VL53L0X di telapak gripper +
  6 sensor induktif LJ12A3 untuk titik nol tiap sendi.
- **Kamera stereo**: produk USB dua lensa yang sama dengan R2, dipasang tetap di tripod di luar jangkauan (eye-to-hand).
  Ketelitian kedalaman ±4 mm di 0,8 m, ±9 mm di 1,2 m, ±18 mm di 1,7 m (ujung terjauh dari tripod)
  (baseline 60 mm, f ≈ 640 px, subpiksel 0,25). Cukup untuk menemukan benda, gripper menutup kesalahan sisa.
- **220 VAC**: kabel berarde → MCB 2P 10 A → kontaktor LC1D09 (rangkaian tahan-diri START + 2 E-stop seri) → 3 driver servo AC.
  PSU Mean Well LRS-200-24 untuk MKS, rem, logika, sensor; buck 6,5 V untuk servo gripper. Relay 24 V membuka rem dari sinyal BRK driver
  (gagal-aman). Semua di box panel 40 × 30 × 18 cm.

### Koreksi terhadap keputusan awal orkestrator (alasan dari hitungan)
1. **J2 bukan 400 W + PLF60-L1.** Torsi bahu perlu 51,9 N·m (statik 45,6 + percepatan 6,4); 400 W × 1:10 × 0,95 = 12,1 N·m.
   PLF60-L1 hanya ada 1:5 dan 1:10. Dipakai **750 W ber-rem + PLF90 2 tahap 1:50** (motor × rasio = 110 N·m, dibatasi torsi gearbox 56 N·m).
2. **J3 bukan 1:10.** Siku perlu 14,3 N·m, sedangkan 400 W × 1:10 = 12,1 N·m (118%). Dipakai **gearbox 60 mm 1:20, 5 arcmin** → 23,4 N·m.
3. **J1 tetap 400 W + PLF60-L1 1:10** (6,7 dari 12,1 N·m).
4. **Gearbox NEMA17 bukan yang murah (PG19, backlash "≤ 1°")**: pas di batas, bukan < 1°. Dipilih FLE42 1:10 (5 N·m); backlash belum tertulis.
5. Varian servo AC 200 W tidak ada di toko yang sama; 400 W tetap dipakai untuk J1 & J3.

### Tabel torsi (lengan terentang horizontal, kasus terburuk)
Massa bergerak 7,8 kg. Kapasitas = torsi **rated** motor × rasio × efisiensi, dibatasi torsi rated gearbox. Percepatan sendi 2/2/3/6/6/6 rad/s².

| Sendi | Penggerak | Statik | Percepatan | Total | Kapasitas | Beban |
|---|---|---|---|---|---|---|
| J1 base | 400 W + PLF60-L1 1:10 | 0 | 6,7 | 6,7 N·m | 12,1 N·m | 55% |
| J2 bahu | 750 W rem + PLF90 1:50 | 45,6 | 6,4 | 51,9 N·m | 56,0 N·m (gearbox) | **93%** |
| J3 siku | 400 W rem + 60 mm 1:20 | 12,7 | 1,6 | 14,3 N·m | 23,4 N·m | 61% |
| J4 putar | NEMA17 + FLE42 1:10 | 0 | ±0 | ±0 | 3,6 N·m | ±1% |
| J5 angguk | NEMA17 + FLE42 1:10 | 1,7 | 0,1 | 1,9 N·m | 3,6 N·m | 52% |
| J6 gripper | NEMA17 + FLE42 1:10 | 0 | ±0 | ±0 | 3,6 N·m | ±0% |

Tanpa beban: J2 82%, J3 48%, J5 27%. Massa titik: lengan atas 0,66 kg, rakitan J3 3,3 kg (motor rem 1,75 + gearbox 1,2 + braket 0,35),
lengan bawah 0,45 kg, J4/J5 0,86 kg, J6 0,75 kg, gripper 0,40 kg (estimasi kelas komponen). Simulasi di halaman menghitung ulang per
pose dari posisi massa di model 3D (selisih ≤ 1 N·m dengan tabel): "Rentang penuh" + gripper menjepit 0,5 kg → J2 46,2 N·m statik (83%);
satu siklus demo ambil-taruh (beban 0,5 kg) → puncak J1 55%, J2 87%, J3 51%, J5 30%.

### Kekakuan & backlash (< 1°)
- Backlash per sendi: J3 5 arcmin (iklan); J1/J2 diasumsikan ≤ 15 arcmin (kelas PLF satu/dua tahap); J4–J6 belum ada data, syarat ke toko ≤ 30 arcmin.
  Semua ≤ 0,5° per sendi. Galat ujung terburuk (jumlah semua sendi) ±10 mm di jangkauan penuh: syarat < 1° terpenuhi, tetapi ini lengan
  peraga, bukan untuk pemasangan presisi.
- Lendutan sudut tabung 50 × 50 × 1,5 di beban penuh: lengan atas 0,05°, lengan bawah 0,02°. Puntir gearbox (kekakuan kelas katalog):
  J2 ±7 arcmin, J3 ±5 arcmin.
- Resolusi enkoder di sisi sendi: J1 1,0″, J2 0,2″, J3 0,5″, J4–J6 0,13′.

## Ketidakpastian
- **J2 93% rated** dengan beban 0,5 kg dan percepatan 2 rad/s² di jangkauan penuh: margin tipis. Torsi 56 N·m diambil dari iklan PLF90 (model 10:1);
  minta data T2N untuk 1:50 sebelum bayar (perlu ≥ 60 N·m). Bila kurang: batasi percepatan J2 ke 1 rad/s² di atas 800 mm (→ 87%),
  atau tambah pegas gas penyeimbang bahu.
- Backlash PLF60-L1, PLF90, dan FLE42 tidak tertulis di iklan. PLF90 & gearbox 60 mm 1:20 = pre-order 15–20 hari.
- Massa motor & gearbox = estimasi kelas, belum ditimbang. Diameter as keluaran PLF90 belum pasti (keyless bushing dipilih saat barang datang).
- Pelat 6 mm dipotong & dibor di bengkel kampus; jasa CNC luar belum masuk RAB. PC lab untuk IK/vision tidak masuk RAB.
