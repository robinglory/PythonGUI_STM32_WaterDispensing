import tkinter as tk
from window1 import Window1  # Import Window1 class from window1.py

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()  # Use grid instead of pack
        self.create_widgets()

    def create_widgets(self):
        self.name_label = tk.Label(self)
        self.name_label["text"] = "Enter your name:"
        self.name_label.grid(row=0, column=0, columnspan=2)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=1, column=0, columnspan=2)

        self.age_label = tk.Label(self)
        self.age_label["text"] = "Enter your age:"
        self.age_label.grid(row=2, column=0, columnspan=2)
        self.age_entry = tk.Entry(self)
        self.age_entry.grid(row=3, column=0, columnspan=2)

        self.button1 = tk.Button(self)
        self.button1["text"] = "Color Entry"
        self.button1["command"] = self.greet_button1
        self.button1.grid(row=4, column=0)

        self.button2 = tk.Button(self)
        self.button2["text"] = "Bom Entry"
        self.button2["command"] = self.greet_button2
        self.button2.grid(row=4, column=1)

        self.button3 = tk.Button(self)
        self.button3["text"] = "Stock Entry"
        self.button3["command"] = self.greet_button3
        self.button3.grid(row=5, column=0)

        self.button4 = tk.Button(self)
        self.button4["text"] = "Dispensing"
        self.button4["command"] = self.greet_button4
        self.button4.grid(row=5, column=1)

    def greet_button1(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if name and age:
            window1 = Window1(self.master, name, age)  # Create an instance of Window1
        else:
            self.error_window()

    def greet_button2(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if name and age:
            self.welcome_window2(name, age)
        else:
            self.error_window()

    def greet_button3(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if name and age:
            self.welcome_window3(name, age)
        else:
            self.error_window()

    def greet_button4(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        if name and age:
            self.welcome_window4(name, age)
        else:
            self.error_window()

    def welcome_window1(self, name, age):
        welcome_root = tk.Toplevel(self.master)
        welcome_root.title("Welcome Page 1")
        welcome_label = tk.Label(welcome_root, text=f"Hello, {name}! You are {age} years old. Welcome to Page 1!")
        welcome_label.pack()

    def welcome_window2(self, name, age):
        welcome_root = tk.Toplevel(self.master)
        welcome_root.title("Welcome Page 2")
        welcome_label = tk.Label(welcome_root, text=f"Hello, {name}! You are {age} years old. Welcome to Page 2!")
        welcome_label.pack()

    def welcome_window3(self, name, age):
        welcome_root = tk.Toplevel(self.master)
        welcome_root.title("Welcome Page 3")
        welcome_label = tk.Label(welcome_root, text=f"Hello, {name}! You are {age} years old. Welcome to Page 3!")
        welcome_label.pack()

    def welcome_window4(self, name, age):
        welcome_root = tk.Toplevel(self.master)
        welcome_root.title("Welcome Page 4")
        welcome_label = tk.Label(welcome_root, text=f"Hello, {name}! You are {age} years old. Welcome to Page 4!")
        welcome_label.pack()

    def error_window(self):
        error_root = tk.Toplevel(self.master)
        error_root.title("Error")
        error_label = tk.Label(error_root, text="Please enter your name and age.")
        error_label.pack()

root = tk.Tk()
app = Application(master=root)
app.mainloop()