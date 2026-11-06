# R2 — Robot berkaki (biped)

Spesifikasi asli (`spesifikasi/robotic_arm_specs.docx`):
- 2 kaki, "6-DOF" (hip roll, hip pitch, knee, ankle pitch, ankle roll)
- Thigh + shank ± 240 (satuan tak disebut)
- Berat ± 6 kg, telapak kaki small pad
- Servo digital 12 VDC, torsi ± 20 kg·cm
- Konstruksi stainless steel / logam campuran
- Pengendali Raspberry Pi
- Baterai LiPo 14,8 V 8000 mAh + BMS
- Sensor: enkoder, ultrasonik, IMU, kamera stereoskopik

## Keputusan
Usulan + RAB Tokopedia (dicek 6 Nov 2026, total ±Rp17,15 jt belum ongkir) ada di docx dan di
`visual/r2-biped.html` (model 3D + simulasi torsi sendi). Status: **usulan awal, belum dikunci**.

- Bentuk humanoid tanpa lengan: 12 servo (6 per kaki, hip yaw ditambahkan), badan berisi elektronik, kepala kamera stereo.
  Lengan = opsi (+6 servo ±Rp4,8 jt).
- Servo bus ST3215 12 V 30 kg·cm dengan enkoder magnetik 12-bit; adapter bus USB ke Pi.
- Berat target ±2,3 kg, bukan 6 kg: di simulasi beban servo tertinggi 27/24/34% stall (jalan/jongkok/satu kaki),
  sedangkan 6 kg → 70/63/87%.
- Raspberry Pi 5 4 GB (2 GB bisa, hemat ±Rp1,4 jt). LiPo 3S 5000 mAh (bukan 4S 8000) supaya servo 12 V dicatu
  langsung tanpa regulator dan bobot turun. Charger iMAX B6AC dipakai bersama R1.
- Rangka aluminium 1,8 mm potong laser; harga per 10 cm² untuk bentuk polos, lubang & tekuk dikonfirmasi ke toko.
