# MODULI
import random
import math
import string
import tkinter as tk
from tkinter import messagebox, ttk
import os

# PATHOVI ZA WORDLISTE
JOHN_LIST_PATH = os.path.expanduser("~/usr/share/wordlists/john.lst")
WIFITE_LIST_PATH = os.path.expanduser("~/usr/share/wordlists/wifite.txt")
ROCKYOU_LIST_PATH = os.path.expanduser("~/usr/share/wordlists/rockyou.txt")

file_name = "passwords5.txt"

# Sve znakove default
znakovi_svi = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?/\\|"
znakovi_brojke = string.digits
znakovi_slova = string.ascii_letters
znakovi_bez_simbola = string.ascii_letters + string.digits

# Trenutni izbor znakova, default svi
trenutni_znakovi = znakovi_svi

# Set za zabranjene lozinke
zabranjene_lozinke = set()

def ucitaj_wordlistu(putanja):
    if os.path.exists(putanja):
        with open(putanja, "r", encoding="utf-8", errors="ignore") as f:
            for linija in f:
                linija = linija.strip()
                if linija:
                    zabranjene_lozinke.add(linija)

def generiraj_lozinku(min_entropija):
    global trenutni_znakovi
    N = len(trenutni_znakovi)
    duzina = max(1, math.ceil(min_entropija / math.log2(N)))

    max_pokusaja = 1000
    for _ in range(max_pokusaja):
        lozinka = ''.join(random.choice(trenutni_znakovi) for _ in range(duzina))
        if lozinka not in zabranjene_lozinke:
            stvarna_entropija = round(duzina * math.log2(N), 2)
            return lozinka, stvarna_entropija

    stvarna_entropija = round(duzina * math.log2(N), 2)
    return lozinka, stvarna_entropija

def ocijeni_entropiju(ent):
    if ent < 40:
        return "Slaba", "red", 20
    elif ent < 60:
        return "Osrednja", "orange", 40
    elif ent < 80:
        return "Dobra", "yellow", 60
    elif ent < 100:
        return "Jaka", "lightgreen", 80
    else:
        return "Vrhunska", "green", 100

def postavi_znakove(vrsta):
    global trenutni_znakovi
    if vrsta == "svi":
        trenutni_znakovi = znakovi_svi
    elif vrsta == "slova":
        trenutni_znakovi = znakovi_slova
    elif vrsta == "brojevi":
        trenutni_znakovi = znakovi_brojke
    elif vrsta == "bez_simbola":
        trenutni_znakovi = znakovi_bez_simbola
    lbl_znakovi.config(text=f"Trenutni znakovi: {len(trenutni_znakovi)}")
    resetiraj()

def prikazi_lozinku(cilj=None):
    if cilj is None:
        try:
            cilj = float(entry_entropija.get())
            if cilj < 20 or cilj > 200:
                raise ValueError
        except ValueError:
            messagebox.showerror("Greška", "Unesite broj između 20 i 200.")
            return

    lozinka, ent = generiraj_lozinku(cilj)
    lbl_lozinka.config(text=f"🔐 Lozinka: {lozinka}")
    lbl_entropija.config(text=f"Entropija: {ent} bita")
    lbl_lozinka.lozinka = lozinka
    btn_kopiraj.config(state=tk.NORMAL)

    ocjena, boja, progress = ocijeni_entropiju(ent)
    traka['value'] = progress
    traka.configure(style=f"{boja}.Horizontal.TProgressbar")
    lbl_ocjena.config(text=f"Ocjena: {ocjena}", fg=boja)

    with open(file_name, "a", encoding="utf-8") as f:
        f.write(f"{lozinka} - {ocjena} ({ent} bita)\n")

def kopiraj():
    root.clipboard_clear()
    root.clipboard_append(lbl_lozinka.lozinka)
    messagebox.showinfo("Kopirano", "Lozinka je kopirana u međuspremnik.")

def resetiraj():
    entry_entropija.delete(0, tk.END)
    lbl_lozinka.config(text="")
    lbl_entropija.config(text="")
    lbl_ocjena.config(text="")
    btn_kopiraj.config(state=tk.DISABLED)
    traka['value'] = 0

def izlaz():
    root.destroy()

def prikazi_povijest(filtriraj_po=None):
    if not os.path.exists(file_name):
        messagebox.showinfo("Povijest", "Datoteka ne postoji.")
        return

    with open(file_name, "r", encoding="utf-8") as f:
        linije = f.readlines()

    if filtriraj_po:
        filtrirane = [l for l in linije if f"- {filtriraj_po}" in l]
    else:
        filtrirane = linije

    if not filtrirane:
        messagebox.showinfo("Povijest", "Nema šifri koje zadovoljavaju filter.")
        return

    prozor = tk.Toplevel(root)
    prozor.title(f"Povijest lozinki - Filter: {filtriraj_po if filtriraj_po else 'Sve'}")
    prozor.geometry("400x300")

    tekst = tk.Text(prozor, wrap=tk.WORD, bg="#222", fg="white")
    tekst.insert(tk.END, "".join(filtrirane))
    tekst.config(state=tk.DISABLED)
    tekst.pack(expand=True, fill="both", padx=10, pady=10)

# GUI setup
root = tk.Tk()
root.title("Generator lozinki s entropijom i filterom")
root.geometry("560x560")
root.resizable(False, False)
root.configure(bg="#2e2e2e")

style = ttk.Style(root)
style.theme_use('clam')
for boja in ['red', 'orange', 'yellow', 'lightgreen', 'green']:
    style.configure(f"{boja}.Horizontal.TProgressbar", troughcolor="#444", background=boja)

tk.Label(root, text="Unesi entropiju (20-200) ili odaberi:", fg="white", bg="#2e2e2e").pack(pady=(10, 5))
entry_entropija = tk.Entry(root, width=10, bg="#555", fg="white", insertbackground="white")
entry_entropija.pack()

tk.Button(root, text="Generiraj lozinku", command=lambda: prikazi_lozinku(None),
          bg="#444", fg="white").pack(pady=8)

frame_gumbi = tk.Frame(root, bg="#2e2e2e")
frame_gumbi.pack()

opcije = [("Slaba\n<40", 35), ("Osrednja\n40–60", 50), ("Dobra\n60–80", 70),
          ("Jaka\n80–100", 90), ("Vrhunska\n>100", 120)]

for i, (tekst, ent) in enumerate(opcije):
    tk.Button(frame_gumbi, text=tekst, width=10,
              command=lambda v=ent: prikazi_lozinku(v),
              bg="#333", fg="white").grid(row=0, column=i, padx=2)

lbl_lozinka = tk.Label(root, text="", fg="lightgreen", bg="#2e2e2e", font=("Courier", 10))
lbl_lozinka.pack(pady=(15, 2))

lbl_entropija = tk.Label(root, text="", fg="lightgray", bg="#2e2e2e")
lbl_entropija.pack()

lbl_ocjena = tk.Label(root, text="", fg="white", bg="#2e2e2e", font=("Arial", 10, "bold"))
lbl_ocjena.pack()

traka = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
traka.pack(pady=10)

btn_kopiraj = tk.Button(root, text="📋 Kopiraj lozinku", command=kopiraj, bg="#555", fg="white", state=tk.DISABLED)
btn_kopiraj.pack(pady=5)

# Odabir znakova
frame_znakovi = tk.LabelFrame(root, text="Izbor znakova", fg="white", bg="#2e2e2e", labelanchor="n")
frame_znakovi.pack(pady=10, fill="x", padx=10)

var_znakovi = tk.StringVar(value="svi")

tk.Radiobutton(frame_znakovi, text="Svi znakovi", variable=var_znakovi,
               value="svi", command=lambda: postavi_znakove("svi"),
               bg="#2e2e2e", fg="white", selectcolor="#444", indicatoron=0, width=12).pack(side="left", padx=5, pady=5)

tk.Radiobutton(frame_znakovi, text="Samo slova", variable=var_znakovi,
               value="slova", command=lambda: postavi_znakove("slova"),
               bg="#2e2e2e", fg="white", selectcolor="#444", indicatoron=0, width=12).pack(side="left", padx=5, pady=5)

tk.Radiobutton(frame_znakovi, text="Samo brojevi", variable=var_znakovi,
               value="brojevi", command=lambda: postavi_znakove("brojevi"),
               bg="#2e2e2e", fg="white", selectcolor="#444", indicatoron=0, width=12).pack(side="left", padx=5, pady=5)

tk.Radiobutton(frame_znakovi, text="Bez simbola", variable=var_znakovi,
               value="bez_simbola", command=lambda: postavi_znakove("bez_simbola"),
               bg="#2e2e2e", fg="white", selectcolor="#444", indicatoron=0, width=12).pack(side="left", padx=5, pady=5)

lbl_znakovi = tk.Label(root, text=f"Trenutni znakovi: {len(trenutni_znakovi)}", fg="white", bg="#2e2e2e")
lbl_znakovi.pack()

# Reset / Povijest / Izlaz
frame_dno = tk.Frame(root, bg="#2e2e2e")
frame_dno.pack(pady=10)

tk.Button(frame_dno, text="🔄 Reset", command=resetiraj, width=12, bg="#444", fg="white").grid(row=0, column=0, padx=5)

filter_var = tk.StringVar(value="Sve")
filter_opcije = ["Sve", "Slaba", "Osrednja", "Dobra", "Jaka", "Vrhunska"]

filter_menu = ttk.OptionMenu(frame_dno, filter_var, "Sve", *filter_opcije)
filter_menu.grid(row=0, column=1, padx=5)

tk.Button(frame_dno, text="📂 Prikaži povijest",
          command=lambda: prikazi_povijest(None if filter_var.get() == "Sve" else filter_var.get()),
          width=15, bg="#555", fg="white").grid(row=0, column=2, padx=5)

tk.Button(frame_dno, text="❌ Izlaz", command=izlaz, width=12, bg="darkred", fg="white").grid(row=0, column=3, padx=5)

# 🟢 Učitavanje zabranjenih lozinki iz wordlista
ucitaj_wordlistu(JOHN_LIST_PATH)
ucitaj_wordlistu(WIFITE_LIST_PATH)
ucitaj_wordlistu(ROCKYOU_LIST_PATH)

root.mainloop()
