from wablast import Blast
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pandas as pd

b = Blast()

def connect():
    b.access()

def impor_kontak():
    filepath = askopenfilename(
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    b.import_contact(filepath)
    lbl_contact["text"] = f'{pd.read_excel(filepath)}'


w = tk.Tk()
w.title("WhatsApp Blast")
w.rowconfigure(0, minsize=500, weight=1)
w.columnconfigure([1, 2], minsize=500, weight=1)

fr_buttons = tk.Frame(w, relief=tk.RAISED)
lbl_contact = tk.Label(w, relief=tk.RIDGE, text="")
lbl_report = tk.Label(w, relief=tk.RIDGE, text="")

btn_connect = tk.Button(fr_buttons, text="Connect", command=connect)
btn_import = tk.Button(fr_buttons, text="Import Contact", command=impor_kontak)
btn_connect.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_import.grid(row=1, column=0, sticky="ew", padx=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
lbl_contact.grid(row=0, column=1, sticky="nsew")
lbl_report.grid(row=0, column=2, sticky="nsew")

w.mainloop()