# P3 — Tangki pencampur

Spesifikasi asli (`spesifikasi/PLC_specs.docx`):
- 2 tangki inlet, masing-masing ±10 liter
- 1 tangki utama ±20 liter dengan katup pembuangan dan piranti pengaduk
- Katup solenoid 12 VDC pada masing-masing tangki inlet
- Motor 24 VDC dilengkapi impeller pada tangki utama
- Sensor level atas dan bawah pada tangki utama
- Elemen pemanas beserta sensor suhu pada tangki utama
- Konstruksi stainless steel
- Panel kontrol elektronik

## Keputusan
Usulan + RAB Tokopedia (dicek 7 Nov 2026, total ±Rp13,92 jt belum ongkir, PLC Rp7,65 jt di antaranya) ada di docx dan di
`visual/p3-pencampur.html` (model 3D + simulasi batch dengan neraca massa & panas, tabel I/O PLC hidup).
Status: **usulan awal, belum dikunci**.

- **PLC** sama untuk P1/P2/P3: Siemens S7-1200 CPU 1214C AC/DC/RLY (6ES7214-1BG40-0XB0). P3 memakai 7 DI, 8 DO, 1 AI;
  AI kedua cadangan untuk sensor level analog. Alternatif murah: Outseal (PLC lokal berbasis Arduino, ladder), tetapi
  tanpa masukan analog 0–10 V bawaan dan bukan standar industri, jadi tidak dipakai di RAB. HMI tidak diminta (opsi).
- **Semua 24 VDC** (menyimpang dari solenoid 12 VDC di spesifikasi): satu catu Mean Well 24 V untuk katup, motor, lampu,
  transmitter, koil relay. 12 V hanya menambah catu kedua tanpa manfaat; keluaran relay PLC menyalakan 24 V langsung.
- **Katup kerja langsung** 2S-160-15 (1/2 inci, inlet) dan 2S-200-20 (3/4 inci, buang), tekanan kerja 0–10 bar. Inlet hanya
  mengalir karena gravitasi (beda tinggi ±8–28 cm air = 0,01–0,03 bar), katup pilot butuh beda tekanan ±0,3 bar dan tidak
  akan membuka. Katup buang solenoid juga, bukan motorized ball valve (±Rp1,3 jt, pre-order); ball valve dipakai bila cairan berserat.
- **Volume batch 16 L (8 + 8)**, bukan 2 × 10 L: 20 L penuh sampai bibir tidak menyisakan ruang riak pengaduk. Takaran =
  waktu buka katup (bawaan 85 s ≈ 8,1 L, dikalibrasi sekali), dibatasi sensor level atas 25 cm (17,7 L) sebagai pengaman.
  PLC tidak mengukur volume; bila takaran presisi diperlukan, tambah sensor level analog ke AI kedua.
- **Tangki** = panci stainless 304 (Ø30 × 30 cm ±21 L dan Ø25 × 25 cm ±12 L), dilubangi hole saw dan dipasangi bulkhead
  SS304 berseal karet. Tidak perlu las. Rak stainless 4 tingkat 80 × 50 × 120 cm: atas inlet + motor, tingkat 3 tangki utama,
  tingkat 2 panel, ember buangan di lantai. Harga fabrikasi = estimasi alat & fitting, belum jasa.
- **Pemanas 1500 W 220 VAC** (daya tidak disebut dosen): 16 L × 4,186 kJ/kg·K × 33 K = 2,2 MJ, ±26 menit dari 27 ke 60 °C
  (simulasi: 26 menit, 0,67 kWh per batch termasuk tahan 5 menit); menahan 60 °C butuh ±90 W (rugi panas). Lewat SSR
  40 A yang dinyalakan PI proporsional waktu (jendela 2 s), overshoot simulasi ±1 °C.
- **Pengaman pemanas berlapis**: RCBO 16 A 30 mA (arus bocor ke air), MCB 10 A khusus pemanas, interlock perangkat keras LSLL
  (float switch ketiga seri di masukan SSR), interlock PLC LSL + motor wajib jalan, relay K1 yang jatuh saat E-stop
  (memutus L dan N pemanas walau SSR rusak tersambung), thermostat KSD301 90 °C reset manual di dinding tangki.
  Rangka, tangki, selubung pemanas, dan box panel diikat ke PE; steker wajib arde.
- **Sensor suhu PT100 + transmitter 0–10 V** (0–100 °C = 0–27648 di %IW64, ±0,2 °C). DS18B20 tidak dipakai karena sinyal
  digital 1-Wire tidak bisa dibaca PLC tanpa modul tambahan.
- **Level**: 3 float switch stainless tipe L dipasang samping: LSL 7 cm, LSLL 7 cm (perangkat keras), LSH 25 cm.
- **Pengaduk**: gearmotor JGB37-555 24 V 167 rpm 15 W (paket bracket + kontrol kecepatan PWM) + as & baling propeller SS304
  Ø100 mm, kopling fleksibel 6/10 mm, bearing KP000. Daya aduk air di 167 rpm < 1 W, motor 15 W cukup dan arusnya
  (±0,6 A) aman untuk keluaran relay PLC 2 A.

## Daftar I/O (S7-1200 1214C)
| Alamat | Tag | Fungsi |
| --- | --- | --- |
| %I0.0 | START | tombol hijau NO; mode manual: lanjut ke langkah berikutnya |
| %I0.1 | STOP | tombol merah NC (1 = tidak ditekan), jeda batch |
| %I0.2 | RESET | tombol biru NO, hapus alarm |
| %I0.3 | AUTO | selector: 1 otomatis, 0 manual (langkah demi langkah) |
| %I0.4 | ESTOP_OK | 24 V setelah kontak NC E-stop (0 = darurat atau kabel putus) |
| %I0.5 | LSL | level bawah 7 cm |
| %I0.6 | LSH | level atas 25 cm |
| %IW64 | TT1 | suhu 0–10 V = 0–100 °C |
| %IW66 | cadangan | sensor level analog (opsi) |
| %Q0.0 | SV_A | katup inlet A |
| %Q0.1 | SV_B | katup inlet B |
| %Q0.2 | SV_D | katup buang |
| %Q0.3 | M1 | motor pengaduk |
| %Q0.4 | HTR | SSR pemanas (lewat kontak LSLL) |
| %Q0.5–0.7 | H_RUN, H_HEAT, H_ALM | lampu hijau, kuning, merah |

Common keluaran grup 1 (Q0.0–Q0.4) dicatu dari 24 V setelah E-stop; lampu (grup 2) tetap hidup supaya alarm terlihat.
Dioda 1N4007 flyback di semua koil dan motor.

Urutan batch: Siap → Isi A (waktu / LSH) → Isi B (waktu / LSH) → Aduk 60 s → Panaskan ke setpoint (LSL + motor wajib) →
Tahan → Kuras (sampai LSL kering + 40 s) → Selesai. Alarm: E-stop, LSL hilang saat memanaskan, suhu > 85 °C.

## Belum pasti
- Daya pemanas, tegangan katup, dan katup buang manual/otomatis belum dikonfirmasi dosen (usulan: 1500 W, 24 V, solenoid).
- Varian & harga varian: motor paket 24 V, katup DC24, panci 25*25/30*30, rak 4T, MCB 4 A/10 A dicek saat pesan.
- Jarak antartingkat rak (±38 cm) harus ≥ 33 cm untuk panci utama; ulir bulkhead (BSP) vs PT100 (NPT) disambung seal tape.
- Elemen pemanas dibuat pesanan (2–3 hari), nepel kuningan 1 inci masuk bulkhead 1 inci: cocokkan ulir dengan toko.
- Lantai/drain lab: ember 20 L hanya menampung satu batch.
