"""Buat spesifikasi/<nama>_usulan.docx dari docx asli dosen (commit 08968cb); file asli tidak disentuh.

    python tools/isi_spesifikasi.py

Tiap baris dosen diganti baris "spek" di tools/usul/<id>.json (format & penomoran dosen dipertahankan),
lalu di bawah tiap alat ditambah tabel rincian harga. RAB dibaca dari PARTS di visual/<id>.html
supaya halaman dan docx selalu sama. Alasan tiap pilihan ada di "usul" json & README robot/*, plc/*.
"""
import io, json, re, pathlib, subprocess
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Twips

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASLI = "08968cb"
T = "https://www.tokopedia.com/"
KOLOM = ["No", "Komponen", "Spesifikasi", "Jml", "Harga satuan", "Subtotal", "Toko"]
LEBAR = [500, 1900, 2810, 500, 1300, 1300, 1050]  # total 9360 twip = lebar isi halaman Letter, margin 1"
CATATAN = "Harga dari Tokopedia, dicek 6–7 November 2026, belum termasuk ongkos kirim dan PPN."


def rp(n): return "Rp" + f"{n:,}".replace(",", ".")


def rab(html):
    """[(grup|None, nama, qty, harga, toko, url, spek)] dari PARTS; GROUPS = id pertama tiap grup."""
    s = (ROOT / "visual" / html).read_text(encoding="utf-8")
    m = re.search(r"const GROUPS = (\{.*?\});", s)
    grup = dict(re.findall(r'(\w+): "([^"]+)"', m.group(1))) if m else {}
    pola = r'\{ id: "(\w+)", nama: "([^"]+)", qty: (\d+), harga: (\d+), toko: "([^"]+)", url: T \+ "([^"]+)",[^\[]*?spek: \[(.*?)\]'
    rows = [(grup.get(i), n, int(q), int(h), t, T + u, "; ".join(re.findall(r'"([^"]+)"', sp)))
            for i, n, q, h, t, u, sp in re.findall(pola, s, re.S)]
    assert len(rows) == s.count('{ id: "'), f"{html}: tidak semua PARTS terbaca"
    return rows


def ganti_teks(p, teks):
    """Ganti isi paragraf, format run pertama (font, tebal) dosen dipertahankan."""
    rs = p.runs
    for r in rs[1:]: r._r.getparent().remove(r._r)
    rs[0].text = teks


def paragraf_setelah(el, parent):
    p = OxmlElement("w:p"); el.addnext(p)
    return docx.text.paragraph.Paragraph(p, parent)


def rapat(p, kanan=False):
    f = p.paragraph_format; f.space_after = Pt(0); f.line_spacing = 1.0
    if kanan: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def sel(cell, teks, bold=False, kanan=False, warna=None):
    p = cell.paragraphs[0]; rapat(p, kanan)
    r = p.add_run(teks); r.bold = bold; r.font.size = Pt(9)
    if warna: arsir(cell, warna)


def arsir(cell, warna):
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), warna)
    cell._tc.get_or_add_tcPr().append(sh)


def tautan(cell, url, teks):
    p = cell.paragraphs[0]; rapat(p)
    rid = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    for tag, val in (("w:color", "0563C1"), ("w:u", "single"), ("w:sz", "18")):
        e = OxmlElement(tag); e.set(qn("w:val"), val); rpr.append(e)
    r.append(rpr); t = OxmlElement("w:t"); t.text = teks; r.append(t); h.append(r); p._p.append(h)


def tabel(d, kolom):
    tb = d.add_table(rows=1, cols=len(kolom))
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER; tb.autofit = False
    b = OxmlElement("w:tblBorders")
    for s in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{s}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "808080"); b.append(e)
    tb._tbl.tblPr.append(b)
    for c, t in zip(tb.rows[0].cells, kolom): sel(c, t, bold=True, warna="D9D9D9")
    trpr = tb.rows[0]._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); trpr.append(h)  # judul kolom berulang tiap halaman
    return tb


def lebar_kolom(tb, lebar):
    for row in tb.rows:
        for c, w in zip(row.cells, lebar): c.width = Twips(w)


def isi_alat(d, P, u):
    h = next(i for i, p in enumerate(P) if p.text.strip().startswith(u["judul_dosen"]))
    for k, teks in enumerate(u["spek"], 1):
        ganti_teks(P[h + k], teks)
    akhir = P[h + len(u["spek"])]
    parent = akhir._parent

    judul = paragraf_setelah(akhir._p, parent)
    judul.paragraph_format.space_before = Pt(8); judul.paragraph_format.keep_with_next = True
    judul.add_run(f"Rincian harga komponen {u['nama'].lower()}").bold = True

    tb = tabel(d, KOLOM); judul._p.addnext(tb._tbl)
    total, no, grup_kini = 0, 0, None
    for grup, nama, q, harga, toko, url, spek in rab(u["html"]):
        if grup and grup != grup_kini:
            cs = tb.add_row().cells; m = cs[0].merge(cs[-1]); sel(m, grup, bold=True, warna="F2F2F2"); grup_kini = grup
        no += 1; sub = q * harga; total += sub
        cs = tb.add_row().cells
        sel(cs[0], str(no), kanan=True); sel(cs[1], nama); sel(cs[2], spek); sel(cs[3], str(q), kanan=True)
        sel(cs[4], rp(harga) if harga else "cek", kanan=True); sel(cs[5], rp(sub) if harga else "cek", kanan=True)
        tautan(cs[6], url, toko)
    cs = tb.add_row().cells; m = cs[0].merge(cs[4])
    sel(m, "TOTAL", bold=True, kanan=True, warna="D9D9D9"); sel(cs[5], rp(total), bold=True, kanan=True, warna="D9D9D9"); arsir(cs[6], "D9D9D9")
    lebar_kolom(tb, LEBAR)

    cat = paragraf_setelah(tb._tbl, parent)
    r = cat.add_run(CATATAN + " Klik nama toko untuk membuka halaman produk."); r.italic = True; r.font.size = Pt(9)
    return total


def main():
    alat = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "tools" / "usul").glob("*.json"))]
    for berkas in dict.fromkeys(u["docx"] for u in alat):
        asli = subprocess.run(["git", "show", f"{ASLI}:spesifikasi/{berkas}"], cwd=ROOT, capture_output=True, check=True).stdout
        d = docx.Document(io.BytesIO(asli)); P = d.paragraphs
        rekap = [(u["nama"], isi_alat(d, P, u)) for u in alat if u["docx"] == berkas]

        jp = d.add_paragraph(); jp.paragraph_format.space_before = Pt(12); jp.paragraph_format.keep_with_next = True
        jp.add_run("Rekapitulasi biaya").bold = True
        tb = tabel(d, ["No", "Alat", "Total"])
        for i, (n, t) in enumerate(rekap, 1):
            cs = tb.add_row().cells; sel(cs[0], str(i), kanan=True); sel(cs[1], n); sel(cs[2], rp(t), kanan=True)
        cs = tb.add_row().cells; m = cs[0].merge(cs[1])
        sel(m, "TOTAL", bold=True, kanan=True, warna="D9D9D9"); sel(cs[2], rp(sum(t for _, t in rekap)), bold=True, kanan=True, warna="D9D9D9")
        lebar_kolom(tb, [600, 5960, 2800])
        r = d.add_paragraph().add_run(CATATAN); r.italic = True; r.font.size = Pt(9)

        keluar = ROOT / "spesifikasi" / berkas.replace(".docx", "_usulan.docx")
        d.save(keluar)
        print(keluar.name, "; ".join(f"{n} {rp(t)}" for n, t in rekap))


if __name__ == "__main__":
    main()
