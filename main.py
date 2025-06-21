import tkinter as tk
from tkinter import ttk

from colorentry import ColorEntryForm
from bomentry import BomEntryForm
from stockentry import StockEntryForm
from dispensing import DispensingForm

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧪 Dispensing Control Panel")
        self.geometry("400x250")
        self.configure(bg="#f7f7f7")
        self.resizable(False, False)

        # Set ttk theme
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=10)
        style.configure("TLabelFrame", background="#f7f7f7", font=("Segoe UI", 12, "bold"))

        # Create a labeled frame for navigation
        button_frame = ttk.LabelFrame(self, text="Main Menu")
        button_frame.pack(expand=True, padx=20, pady=30)

        # Create buttons
        ttk.Button(button_frame, text="🎨 Color Entry", command=self.open_color_entry).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="📋 BOM Entry", command=self.open_bom_entry).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(button_frame, text="📦 Stock Entry", command=self.stock_entry).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(button_frame, text="⚙️ Dispensing", command=self.dispensing).grid(row=1, column=1, padx=10, pady=10)

        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def open_color_entry(self):
        ColorEntryForm(self)

    def open_bom_entry(self):
        BomEntryForm(self)

    def stock_entry(self):
        StockEntryForm(self)

    def dispensing(self):
        DispensingForm(self)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
