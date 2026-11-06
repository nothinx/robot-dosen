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
- Pengendali sendi: STM32 Black Pill WeAct F411CEU6, sama dengan R1 (satu toolchain & suku cadang). IK/vision tetap di PC/Pi.
_Belum ada; didiskusikan satu per satu. Temuan awal: lihat `KONTEKS.md` bagian Robot._
