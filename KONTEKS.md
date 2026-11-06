# robot-dosen — permintaan dosen: 3 stasiun PLC + 3 robot

Sumber: `spesifikasi/PLC_specs.docx`, `spesifikasi/robotic_arm_specs.docx` (salinan dari Downloads, 6 Nov 2026).
Repo: https://github.com/nothinx/robot-dosen (public, disetujui user 6 Nov 2026) · Pages: https://nothinx.github.io/robot-dosen/
(`visual/r1-beroda.html`, model 3D + simulasi R1). Status: **analisis awal**, belum ada keputusan lingkup/anggaran/tenggat.

Gaya teksnya ("Memiliki …", nilai ±) mirip **spesifikasi teknis pengadaan/hibah alat lab**, bukan dokumen desain.
Jadi pertanyaan pertama: dosen minta kita **membangun** alatnya, atau **menyusun usulan/RAB/desain** saja?

## Ringkasan isi

| # | Alat | Inti spesifikasi |
|---|---|---|
| P1 | Konveyor pengepakan | infeed 1500×100 mm + packing 2000×600 mm, 20 kg/konveyor; fotoelektrik, proksimitas, load cell, enkoder; motor 24 VDC + girboks; katup pneumatik; SS |
| P2 | Konveyor sortir | 3000×200 mm, 20 kg, bin normal + reject; fotoelektrik, warna, kamera, enkoder; motor 24 VDC; katup pneumatik; SS |
| P3 | Tangki pencampur | 2 inlet 10 L + utama 20 L (pengaduk, katup buang); solenoid 12 VDC; motor 24 VDC + impeller; level atas/bawah; pemanas + sensor suhu; SS |
| R1 | Robot beroda | diff-drive 2 roda + kaster, base 350×250 mm, roda Ø80, beban 5 kg; motor 12 VDC 200 rpm, H-bridge 30 A; Arduino Mega; LiPo 4S 5000 mAh + BMS; enkoder, bumper, ultrasonik, IR |
| R2 | Robot berkaki (biped) | 2 kaki, "6-DOF", paha+betis 240, berat 6 kg; servo digital 12 V 20 kg·cm; Raspberry Pi; LiPo 4S 8000 mAh; enkoder, ultrasonik, IMU, kamera stereo |
| R3 | Lengan robot | 6-DOF, jangkauan 1000 mm, rangka aluminium, gripper; servo digital ber-enkoder (posisi/kecepatan/torsi); Arduino Mega; backlash < 1°; enkoder, kamera stereo, proksimitas; 220 VAC |

Catatan: file `robotic_arm_specs.docx` berisi **tiga** robot, bukan hanya lengan.

## Temuan teknis (yang perlu dikonfirmasi ke dosen)

### Stasiun PLC
1. **Merek/tipe PLC, HMI, dan jumlah I/O tidak disebut** — padahal judulnya "PLC". Ini penentu biaya terbesar
   (Siemens S7-1200 / Omron / Mitsubishi FX / Outseal lokal beda jauh). Satu PLC per stasiun atau satu PLC bersama?
2. **Pneumatik butuh kompresor + FRL (filter-regulator-lubricator)** — tidak tercantum. Tegangan koil katup juga tidak.
3. **P2 berat ±6 kg tidak masuk akal** untuk konveyor stainless 3 m (pelat alasnya saja ±7 kg). Kemungkinan salah ketik
   (60 kg?) atau maksudnya berat benda uji.
4. **P1 "diameter kapasitas ±20 kg"** — salah ketik, maksudnya "kapasitas beban".
5. **Kamera di P2**: PLC tidak memproses gambar. Perlu sensor vision mandiri (keluaran OK/NG digital) atau PC/Pi
   yang mengirim hasil ke PLC (Modbus TCP/digital I/O).
6. **P3 solenoid 12 VDC** sementara lainnya 24 VDC → dua rail catu. Usul: semua 24 VDC (standar keluaran PLC).
   Inlet mengalir gravitasi → pilih katup **zero-differential / direct-acting**; katup pilot butuh beda tekanan.
7. **P3 volume**: 2 × 10 L masuk ke tangki 20 L = penuh sampai bibir. Takaran harus dibatasi level sensor / timer.
8. **Pemanas P3** daya & tegangan tidak disebut. Gambaran: 20 L air dari 25→60 °C ≈ 2,9 MJ → ±50 menit dengan 1 kW.
   Hampir pasti 220 VAC lewat SSR/kontaktor; wajib interlock "level bawah" (anti dry-run) + thermostat pengaman.
9. **Load cell (P1) dan sensor suhu (P3) = masukan analog** (perlu amplifier 4–20 mA/0–10 V atau modul RTD);
   **enkoder = high-speed counter**. Pastikan PLC yang dipilih punya keduanya.
10. Katup pembuangan P3: manual atau solenoid? Kecepatan motor konveyor: tetap atau diatur (PWM/analog)?

Perkiraan I/O kasar (untuk memilih PLC): P1 ≈ 6 DI + 2 HSC + 1 AI / 5 DO · P2 ≈ 5 DI + 1 HSC / 3 DO ·
P3 ≈ 2 DI + 1 AI / 5 DO. Per stasiun cukup PLC kelas 14 DI/10 DO + 2 AI (mis. S7-1214C DC/DC/DC).

### Robot
1. **R1 motor 12 V di baterai 4S (14,8 V nominal, 16,8 V penuh)** → batasi duty PWM ±70% atau pakai motor 24 V.
   Kecepatan teoretis π·0,08·200/60 ≈ **0,84 m/s** — wajar. Rangka stainless membuat berat; aluminium lebih masuk akal.
2. **R2 jumlah sendi tidak konsisten**: tertulis 6-DOF tapi hanya 5 sendi (hip roll, hip pitch, knee, ankle pitch,
   ankle roll) — kurang **hip yaw**. 6 per kaki (12 servo) atau total? Satuan "240" tidak disebut (mm?).
3. **R2 torsi servo kurang**: 20 kg·cm = 1,96 N·m. Robot 6 kg dengan lengan momen 5–10 cm di lutut/pinggul
   saat jongkok/satu kaki = 2,9–5,9 N·m. Pilihan: turunkan berat ke ±2–3 kg, atau servo ≥ 50 kg·cm.
   Stainless untuk biped terlalu berat — pakai aluminium.
4. **R2 "servo 12 V ber-enkoder"** artinya servo bus pintar (Dynamixel/Feetech seri 12 V), bukan servo PWM hobi.
   Raspberry Pi butuh adapter bus (U2D2/URT-1); 16,8 V baterai penuh melebihi 12 V → perlu regulator arus besar.
5. **R3 beban (payload) tidak disebut** — ini parameter terpenting lengan. Contoh: 0,5 kg di ujung 1 m + bobot lengan
   → momen bahu statis ±15–20 N·m. Servo hobi/smart kelas menengah tidak sanggup; perlu stepper/BLDC + reducer
   (planetary/cycloidal/harmonic). Jangkauan 1 m dengan servo = bagian paling mahal & berisiko.
6. **R3 backlash < 1°** longgar untuk jangkauan 1 m: 1° di 1 m ≈ 17 mm galat di ujung, per sendi. Cukup untuk
   peraga, tidak untuk pick-and-place presisi.
7. **R3 Arduino Mega** (8-bit, 16 MHz, tanpa FPU) lemah untuk IK 6-DOF + kamera stereo. Usul: Mega sebagai
   pengendali sendi saja, IK & vision di PC/Raspberry Pi (ROS 2/MoveIt).
8. Keselamatan: tombol **E-stop** perangkat keras untuk R3 (220 VAC) dan semua stasiun PLC — belum disebut.

## Yang belum diketahui (tanyakan ke dosen)
- Tujuan: alat praktikum lab, hibah/pengadaan, lomba, atau penelitian? Berapa unit?
- Lingkup kita: rancang + bangun fisik + program, atau dokumen usulan/RAB/gambar saja? Modul praktikum?
- Anggaran dan tenggat; siapa yang membeli komponen; ada bengkel fabrikasi stainless?
- Merek PLC/HMI yang diinginkan (atau mengikuti yang sudah ada di lab).
- Payload R3, jumlah servo R2, daya pemanas P3, tegangan katup pneumatik.

## Hubungan dengan proyek lain
Pengalaman servo & IK ada di `projects/Hexapod_KRSRI_2026`; Modbus/integrasi PLC bisa dicoba di `projects/iot-lab`
(skill `iot-bas`).
