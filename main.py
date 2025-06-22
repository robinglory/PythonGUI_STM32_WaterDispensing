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
        self.geometry("500x350")
        self.configure(bg="#1e1e2f")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#3e3e50", foreground="white")
        style.map("TButton",
            background=[("active", "#5c5c77")],
            foreground=[("disabled", "#a0a0a0")])
        style.configure("TLabelFrame", background="#1e1e2f", foreground="white", font=("Segoe UI", 13, "bold"))

        # Title Label
        title_label = tk.Label(self, text="🎨 Color Dispensing Control Panel", font=("Segoe UI", 16, "bold"), fg="white", bg="#1e1e2f")
        title_label.pack(pady=(20, 5))

        subtitle_label = tk.Label(self, text="Created by Yan Naing Kyaw Tint\nVI McE-5", font=("Segoe UI", 11), fg="lightgray", bg="#1e1e2f")
        subtitle_label.pack(pady=(0, 20))

        button_frame = ttk.LabelFrame(self, text="Main Menu")
        button_frame.pack(expand=True, padx=20, pady=10)

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
