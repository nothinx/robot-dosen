# R1 — Robot beroda

Spesifikasi asli (`spesifikasi/robotic_arm_specs.docx`):
- Sasis differential-drive, 2 roda + 1 kaster
- Base (p × l) ± 350 × 250 mm, roda Ø ± 80 mm
- Kapasitas angkut sampai 5 kg
- Motor 12 VDC ± 200 rpm, driver dual H-bridge sampai 30 A
- Konstruksi stainless steel / logam campuran
- Pengendali Arduino Mega
- Baterai LiPo 14,8 V 5000 mAh + BMS
- Sensor: enkoder, benturan, ultrasonik, inframerah

## Keputusan
Usulan lengkap + RAB Tokopedia (dicek 6 Nov 2026, total ±Rp4,69 jt belum ongkir) ditulis langsung di
`spesifikasi/robotic_arm_specs.docx`, di bawah tiap baris spesifikasi dosen (teks biru). User diberi izin dosen
mengubah spesifikasi dengan alasan. Status: **usulan awal, belum dikunci**.

- Pengendali: STM32 Nucleo-F446RE (ganti Arduino Mega).
- Motor: PG36 24 V 1:50,1 + enkoder 7 PPR (tegangan & rpm menyimpang dari spesifikasi; alasan di docx).
- Driver: Cytron MDD10A (10 A kontinu / 30 A puncak); MDDS30 bila 30 A kontinu wajib.
- Rangka aluminium 3 mm; roda RC 85 mm + hex coupling 8 mm; kaster PU 1,5".
