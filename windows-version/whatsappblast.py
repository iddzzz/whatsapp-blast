import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import TclError
from wablast import Blast, BlastData
import pandas as pd

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.b = None
        self.data = BlastData()

        self.parent.title("WhatsApp Blast")
        self.parent.rowconfigure(0, minsize=500, weight=1)
        self.parent.columnconfigure([1, 2], minsize=500, weight=1)

        # Frames
        self.fr_buttons = tk.Frame(self, relief=tk.RAISED)
        self.txt_contact = tk.Text(self, relief=tk.RIDGE)
        self.fr_additional = tk.Frame(self, relief=tk.RIDGE)

        # Buttons on fr_buttons
        self.btn_connect = tk.Button(self.fr_buttons, text="Connect", command=self.connect)
        self.btn_import = tk.Button(self.fr_buttons, text="Import Contact", command=self.impor_kontak)
        self.btn_connect.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_import.grid(row=1, column=0, sticky="ew", padx=5)

        # Elements on fr_additional
        self.lbl_from = tk.Label(self.fr_additional, text="From (Group/Person)")
        self.entry_from = tk.Entry(self.fr_additional)
        self.lbl_num_msg = tk.Label(self.fr_additional, text="Number of messages")
        self.entry_num = tk.Entry(self.fr_additional)
        self.btn_forward = tk.Button(self.fr_additional, text="Forward", command=self.forward)

        self.lbl_from.grid(row=0, column=0, sticky="ew", padx=5)
        self.entry_from.grid(row=0, column=1, sticky="ew", padx=5)
        self.lbl_num_msg.grid(row=1, column=0, sticky="ew", padx=5)
        self.entry_num.grid(row=1, column=1, sticky="ew", padx=5)
        self.btn_forward.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Master attachment
        self.fr_buttons.grid(row=0, column=0, sticky="ns")
        self.txt_contact.grid(row=0, column=1, sticky="nsew")
        self.fr_additional.grid(row=0, column=2, sticky="nsew")

    def connect(self):
        if self.b is None:
            self.b = Blast()
            self.b.access()
            self.btn_connect["text"] = "Disconnect"
        else:
            self.b.close()
            self.btn_connect["text"] = "Connect"
            self.b = None

    def impor_kontak(self):
        filepath = askopenfilename(
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        self.data.import_contact(filepath)
        try:
            self.txt_contact.delete(0, tk.END)
        except TclError:
            pass
        for name in self.data.contact:
            self.txt_contact.insert(tk.END, f'{name}\n')

    def forward(self):
        try:
            from_who = self.entry_from.get()
            num = int(self.entry_num.get())
            target = self.data.contact
        except:
            print('Forward Failed')
            return

        if all([from_who, num, all(target)]):
            self.b.forward(from_who, num, target)
        else:
            print('Harus ada dari, jumlah, target')

        return


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()