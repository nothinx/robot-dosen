"""Tulis "Spesifikasi kami" + tabel RAB R1 & R2 ke spesifikasi/robotic_arm_specs.docx.

Selalu mulai dari docx asli dosen (commit 08968cb), lalu:
    git --no-pager show 08968cb:spesifikasi/robotic_arm_specs.docx > spesifikasi/robotic_arm_specs.docx
    python tools/isi_spesifikasi.py
RAB dibaca dari daftar PARTS di visual/r1-beroda.html & visual/r2-biped.html supaya halaman dan docx selalu sama.
"""
import copy, re, pathlib
import docx
from docx.shared import RGBColor, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "spesifikasi" / "robotic_arm_specs.docx"
BIRU = RGBColor(0x1F, 0x4E, 0x79)
T = "https://www.tokopedia.com/"

def rab(html):
    s = (ROOT / "visual" / html).read_text(encoding="utf-8")
    pola = r'nama: "([^"]+)", qty: (\d+), harga: (\d+), toko: "([^"]+)", url: T \+ "([^"]+)"'
    return [(n, int(q), int(h), t, p) for n, q, h, t, p in re.findall(pola, s)]

# kunci = nomor baris spesifikasi dosen di bawah judul robot (1 = baris pertama)
USUL_R1 = {
    1: ["Tetap differential-drive. Kaster: roda kastor PU 1,5\" putar, double bearing (ball caster kecil tidak kuat untuk total ±13 kg)."],
    2: ["Tetap 350 × 250 mm. Dua dek pelat aluminium 3 mm (dek bawah: semua elektronik; dek atas: bak muatan).",
        "Bak muatan 270 × 250 mm di dek atas, dinding siku aluminium 20 × 20 × 2 mm di 4 sisi, alas karet anti-slip, lubang tali pengikat. Pola sama dengan Kobuki/TurtleBot 2 (muatan 5 kg) dan Pioneer 3-DX: elektronik di bawah, permukaan teratas kosong untuk barang. Ultrasonik dipasang di celah antar dek supaya tidak terhalang muatan; E-stop di jalur 80 mm belakang bak."],
    3: ["Roda RC Ø85 mm ban karet (masih dalam toleransi ±; roda robot 80 mm di pasaran hampir semuanya mecanum).",
        "Sambungan: hex coupling kuningan lubang 8 mm → hex 12 mm (poros PG36 8 mm, velg RC hex 12 mm)."],
    4: ["Tetap 5 kg. Dasar perhitungan: massa total ±13 kg, torsi puncak ±6,5 kg·cm per motor (tanjakan 10° + percepatan 0,5 m/s²).",
        "Pusat bak 30 mm di belakang poros roda: dengan muatan 5 kg ±77% berat jatuh di roda penggerak (traksi baik), titik berat ±14 cm dari lantai, robot baru terjungkit ke depan pada perlambatan ±3 m/s² (rem simulasi 0,5 m/s²)."],
    5: ["Motor: planetary PG36 rasio 1:50,1 + enkoder 7 PPR, varian 24 V, 2 unit, dengan braket dudukan.",
        "Alasan: motor 12 V di baterai 4S (16,8 V penuh) bekerja di atas tegangan nominal. Motor 24 V di 14,8 V berjalan dingin, "
        "torsi stall ±25 kg·cm (≥ 3× kebutuhan), kecepatan ±150 rpm tanpa beban ≈ 0,6 m/s. Kalau 200 rpm wajib: baterai 6S, atau motor 12 V dengan PWM dibatasi 70%.",
        "Enkoder: 7 PPR × 50,1 × 4 tepi = ±1400 count/putaran roda (±0,19 mm/count), dibaca timer STM32 mode enkoder.",
        "Driver: Cytron MDD10A dual channel, 10 A kontinu / 30 A puncak, 5–30 V. Kebutuhan nyata ±1–3 A per motor. "
        "Bila 30 A kontinu wajib: Cytron MDDS30."],
    6: ["Aluminium 3 mm (opsi \"logam campuran\" di spesifikasi). Stainless menambah ±3–4 kg tanpa manfaat fungsional."],
    7: ["Diganti STM32 Black Pill WeAct STM32F411CEU6 (Cortex-M4 100 MHz + FPU, 512 KB flash, 128 KB RAM), ditancap di PCB pembawa "
        "(konektor motor, sensor, catu). Pemrograman/debug lewat ST-Link V2.",
        "Alasan: 8 timer perangkat keras cukup untuk 2 enkoder kuadratur (mode enkoder), PWM 2 motor, dan input capture 3 ultrasonik; "
        "bisa diprogram dengan Arduino IDE (STM32duino) maupun STM32CubeIDE. Pengendali yang sama dipakai di lengan robot (R3)."],
    8: ["LiPo 4S 5000 mAh 70C (CNHL, konektor XT90). Pack hobi tidak punya BMS, jadi ditambah BMS 4S 30A (proteksi over/under-voltage & arus).",
        "Pengisian dengan balance charger iMAX B6AC (catu AC bawaan). Tambahan pengaman: sekring 15 A + tombol E-stop di jalur daya motor.",
        "Catu logika: buck XL4015 5 A, 14,8 V → 5 V (Black Pill, sensor).",
        "Saklar utama rocker 16 A, kabel daya silikon 12 AWG, konektor XT90; sensor & enkoder lewat konektor JST XH ke PCB pembawa."],
    9: ["Enkoder: bawaan motor (2). Benturan: limit switch roller Omron V-156 (2, depan kiri/kanan).",
        "Ultrasonik: HC-SR04 versi 3,3–5 V (3: depan, kiri-depan, kanan-depan; aman untuk I/O 3,3 V STM32).",
        "Inframerah: modul TCRT5000 (2, deteksi tepi/garis)."],
}

USUL_R2 = {
    1: ["12 sendi, 6 per kaki: hip yaw, hip roll, hip pitch, lutut, ankle pitch, ankle roll. Daftar dosen baru berisi 5 sendi padahal tertulis 6-DOF; "
        "hip yaw ditambahkan supaya robot bisa berbelok. Bentuk humanoid: badan menampung elektronik, kepala membawa kamera stereo. "
        "Lengan belum termasuk (opsi: 3 servo per lengan, tambah ±Rp4,8 jt)."],
    2: ["Paha 120 mm + betis 120 mm (sumbu ke sumbu), tinggi robot ±0,55 m."],
    3: ["Target ±2,3 kg (estimasi dari komponen). Alasan, dihitung di simulasi (visual/r2-biped.html, torsi statik terhadap stall servo 2,94 N·m): "
        "berat 2,3 kg → beban servo tertinggi 27% saat jalan, 24% jongkok, 34% berdiri satu kaki; berat 6 kg → 70%, 63%, 87%. "
        "Saat melangkah beban dinamis 1,5–2× angka statik, jadi 6 kg melewati kemampuan servo kelas ini; sasaran kerja ≤ 50% stall."],
    4: ["Telapak pelat aluminium 120 × 70 mm + alas karet anti-slip."],
    5: ["Servo bus ST3215 12 V 30 kg·cm (2,94 N·m), 12 unit: enkoder magnetik 12-bit (4096 posisi, 0,088°), umpan balik posisi, kecepatan, beban, suhu; "
        "satu jalur bus TTL 1 Mbps. Dipilih 30 kg·cm (di atas 20 kg·cm) karena perhitungan baris berat. "
        "Servo PWM biasa lebih murah tetapi tanpa umpan balik dan bukan 12 V."],
    6: ["Aluminium 1,8 mm potong laser (pesan custom), ditekuk jadi braket U/L. Stainless setebal sama ±3× lebih berat."],
    7: ["Raspberry Pi 5 4 GB + active cooler + microSD 64 GB. Servo dikendalikan lewat adapter bus servo USB; IMU lewat I2C; kamera lewat USB. "
        "Pi 5 2 GB menghemat ±Rp1,4 jt bila tidak memakai ROS 2."],
    8: ["LiPo 3S 11,1 V 5000 mAh + BMS 3S 40 A. Alasan: servo ST3215 versi 12 V dicatu ±12 V; 4S penuh 16,8 V melebihinya dan butuh regulator 12 V ±15 A. "
        "3S penuh 12,6 V langsung ke servo tanpa regulator. 5000 mAh dipilih karena bobot (±0,4 kg, 4S 8000 mAh ±0,75 kg); estimasi waktu jalan ±60 menit.",
        "Pi dicatu buck 5 V 5 A; saklar utama, sekring 15 A, kabel 12 AWG. Pengisian memakai charger iMAX B6AC milik robot beroda."],
    9: ["Enkoder: bawaan tiap servo (12). Ultrasonik: HC-SR04 3,3 V di dada. IMU: BNO085 9-sumbu, fusi sensor di dalam chip (kuaternion langsung). "
        "Kamera stereoskopik: modul USB dua lensa 2560 × 720, 30 fps, kedua lensa tersinkron dalam satu frame."],
}

ROBOT = [
    ("Robot beroda", USUL_R1, "r1-beroda.html", "Robot beroda"),
    ("Robot berkaki", USUL_R2, "r2-biped.html", "Robot berkaki"),
]

def rp(n): return "Rp" + f"{n:,}".replace(",", ".")

d = docx.Document(SRC)
P = d.paragraphs
anchor_ref = None
def sisip_setelah(anchor_el, teks, label):
    """Paragraf bullet level-2 (numId sama dengan anchor) berwarna biru."""
    src = anchor_ref._p  # paragraf dosen asli, sumber numPr
    p = OxmlElement("w:p")
    anchor_el.addnext(p)
    para = docx.text.paragraph.Paragraph(p, anchor_ref._parent)
    ppr = copy.deepcopy(src.pPr)
    for r in ppr.findall(qn("w:rPr")): ppr.remove(r)
    ppr.find(qn("w:numPr")).find(qn("w:ilvl")).set(qn("w:val"), "1")
    p.insert(0, ppr)
    if label:
        r = para.add_run("Spesifikasi kami: "); r.bold = True; r.font.color.rgb = BIRU
    r = para.add_run(teks); r.font.color.rgb = BIRU
    return p

def link(par, url, teks):
    rid = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "0563C1"); rpr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "18"); rpr.append(sz)
    r.append(rpr); t = OxmlElement("w:t"); t.text = teks; r.append(t); h.append(r); par._p.append(h)

def isi_robot(judul_dosen, USUL, html, nama):
    global anchor_ref
    h = next(i for i, p in enumerate(P) if p.text.strip().startswith(judul_dosen))
    assert "Spesifikasi kami" not in P[h + 1].text, "docx sudah terisi; mulai dari versi asli"
    for idx in sorted(USUL, reverse=True):
        anchor_ref = P[h + idx]
        el = anchor_ref._p
        for i, t in enumerate(USUL[idx]):
            el = sisip_setelah(el, t, i == 0)
    blok_akhir = P[h + max(USUL)]._p
    while blok_akhir.getnext() is not None and blok_akhir.getnext().find(qn("w:pPr") + "/" + qn("w:numPr")) is not None             and blok_akhir.getnext().find(qn("w:pPr") + "/" + qn("w:numPr") + "/" + qn("w:ilvl")).get(qn("w:val")) == "1":
        blok_akhir = blok_akhir.getnext()
    judul = OxmlElement("w:p"); blok_akhir.addnext(judul)
    jp = docx.text.paragraph.Paragraph(judul, P[h]._parent)
    jp.paragraph_format.space_before = Pt(10)
    r = jp.add_run(f"Rincian komponen & harga {nama} (Tokopedia, dicek 6 Nov 2026, belum termasuk ongkir)")
    r.bold = True; r.font.color.rgb = BIRU
    RAB = rab(html)
    kolom = ["No", "Komponen", "Qty", "Harga satuan", "Subtotal", "Toko (tautan)"]
    lebar = [450, 3600, 450, 1300, 1300, 2100]
    tbl = d.add_table(rows=1, cols=len(kolom))
    judul.addnext(tbl._tbl)
    tblPr = tbl._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for s in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{s}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "999999"); b.append(e)
    tblPr.append(b)

    def isi(cell, teks, bold=False, kanan=False):
        p = cell.paragraphs[0]; r = p.add_run(teks); r.bold = bold; r.font.size = Pt(9)
        if kanan: p.alignment = 2
        return p

    for c, t in zip(tbl.rows[0].cells, kolom): isi(c, t, bold=True)
    total = 0
    for i, (nama, q, h, toko, path) in enumerate(RAB, 1):
        sub = q * h; total += sub
        cs = tbl.add_row().cells
        isi(cs[0], str(i)); isi(cs[1], nama); isi(cs[2], str(q), kanan=True)
        isi(cs[3], rp(h) if h else "cek", kanan=True); isi(cs[4], rp(sub) if h else "cek", kanan=True)
        link(cs[5].paragraphs[0], T + path, toko)
    cs = tbl.add_row().cells
    isi(cs[1], "TOTAL (perkiraan)", bold=True); isi(cs[4], rp(total), bold=True, kanan=True)
    for row in tbl.rows:
        for c, w in zip(row.cells, lebar): c.width = docx.shared.Twips(w)
    return total

for r in ROBOT:
    print(r[3], rp(isi_robot(*r)))
d.save(SRC)
