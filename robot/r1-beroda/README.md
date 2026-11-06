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
Usulan lengkap + RAB Tokopedia (dicek 6 Nov 2026, total ±Rp4,90 jt belum ongkir, termasuk kabel, konektor, spacer, PCB pembawa) ditulis langsung di
`spesifikasi/robotic_arm_specs.docx`, di bawah tiap baris spesifikasi dosen (teks biru). User diberi izin dosen
mengubah spesifikasi dengan alasan. Status: **usulan awal, belum dikunci**.

- Pengendali: STM32 Black Pill WeAct F411CEU6 + ST-Link V2 (ganti Arduino Mega). Nucleo ditolak: berlebihan & 3× harga.
- Motor: PG36 24 V 1:50,1 + enkoder 7 PPR (tegangan & rpm menyimpang dari spesifikasi; alasan di docx).
- Driver: Cytron MDD10A (10 A kontinu / 30 A puncak); MDDS30 bila 30 A kontinu wajib.
- Rangka aluminium 3 mm; roda RC 85 mm + hex coupling 8 mm; kaster PU 1,5".
- Muatan 5 kg: dek atas = bak 270 × 250 mm (siku aluminium 20 × 20 × 2 + alas karet anti-slip); semua elektronik di
  dek bawah, ultrasonik di celah antar dek, E-stop di jalur 80 mm belakang bak. Acuan: Kobuki/TurtleBot 2 (5 kg),
  Pioneer 3-DX. Pusat bak 30 mm di belakang poros roda → ±77% berat di roda penggerak.
