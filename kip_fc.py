"""Sistem pakar sederhana: kelayakan calon penerima KIP Kuliah 2026.

Pakai:
    python kip_fc.py              # interaktif (jawab y/t)
    python kip_fc.py --kasus 1    # jalankan kasus uji nomor 1..4 dari kb_kip.json
"""
import argparse
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def muat(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb_kip.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def terpenuhi(aturan, memori):
    """mode "dan": semua syarat ada di memori; mode "atau": salah satu cukup."""
    cek = all if aturan["mode"] == "dan" else any
    return cek(p in memori for p in aturan["jika"])


def maju(kb, fakta_awal):
    """Forward chaining. Kembalikan (memori, asal, log)."""
    memori = set(fakta_awal)
    asal = {}      # fakta hasil -> aturan yang menghasilkannya (bahan "alasan")
    log = []
    siklus = 0
    while True:
        cocok = [a for a in kb["aturan"]
                 if a["maka"] not in memori and terpenuhi(a, memori)]
        if not cocok:
            break
        r = cocok[0]
        siklus += 1
        memori.add(r["maka"])
        asal[r["maka"]] = r
        log.append(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
    log.append(f"Siklus {siklus + 1}: tidak ada aturan baru, berhenti")
    return memori, asal, log


def jelaskan(fakta, asal, memori, tingkat=0):
    pad = "  " * tingkat
    r = asal.get(fakta)
    if r is None:
        print(f"{pad}{fakta}  [fakta dari user]")
        return
    benar = [p for p in r["jika"] if p in memori]
    print(f"{pad}{fakta}  <- {r['id']} ({', '.join(benar)}) [{r['sumber']}]")
    for p in benar:
        jelaskan(p, asal, memori, tingkat + 1)


def fakta_dasar(kb):
    hasil = {a["maka"] for a in kb["aturan"]}
    return [f for f in kb["pertanyaan"] if f not in hasil]


def tanya(kb, jawaban_otomatis=None):
    print(kb["judul"])
    print("Jawab y/t.")
    ya = []
    for i, f in enumerate(fakta_dasar(kb), 1):
        if jawaban_otomatis is None:
            j = ""
            while j not in ("y", "t"):
                j = input(f"{i}. {kb['pertanyaan'][f]} (y/t) > ").strip().lower()
        else:
            j = "y" if f in jawaban_otomatis else "t"
            print(f"{i}. {kb['pertanyaan'][f]} (y/t) > {j}")
        if j == "y":
            ya.append(f)
    return ya


def laporkan(kb, ya):
    memori, asal, log = maju(kb, ya)
    print()
    print("Fakta awal:", ", ".join(ya) if ya else "(tidak ada)")
    print()
    for baris in log:
        print(baris)
    print()
    akhir = kb["kesimpulan_akhir"]
    turunan = [f for f in asal]
    if akhir in memori:
        print(f"Kesimpulan: {akhir}")
        print("Alasan:")
        jelaskan(akhir, asal, memori, 1)
        if "ekonomi prioritas 3" in memori and not (
                "ekonomi prioritas 1" in memori or "ekonomi prioritas 2" in memori):
            print("Catatan: prioritas 3 bergantung ketersediaan kuota.")
    elif turunan:
        print("Kesimpulan: belum layak diusulkan (syarat belum lengkap)")
        print("Yang sudah terpenuhi:")
        for f in turunan:
            jelaskan(f, asal, memori, 1)
    else:
        print("Kesimpulan: tidak ada kesimpulan yang dapat ditarik dari fakta tersebut")
    print()
    print("Catatan:", kb["batas"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kasus", type=int, help="nomor kasus uji (1..n)")
    ap.add_argument("--kb", default=None)
    arg = ap.parse_args()
    kb = muat(arg.kb)
    if arg.kasus:
        k = kb["kasus_uji"][arg.kasus - 1]
        print(f"[Kasus uji {arg.kasus}] {k['nama']}")
        ya = tanya(kb, jawaban_otomatis=set(k["ya"]))
    else:
        ya = tanya(kb)
    laporkan(kb, ya)


if __name__ == "__main__":
    main()
