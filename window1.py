import tkinter as tk

class Window1:
    def __init__(self, master, name, age):
        self.master = master
        self.name = name
        self.age = age
        self.create_window()

    def create_window(self):
        welcome_root = tk.Toplevel(self.master)
        welcome_root.title("Welcome Page 1")

        # Create labels and entries for different information
        self.city_label = tk.Label(welcome_root, text="Enter your city:")
        self.city_label.pack()
        self.city_entry = tk.Entry(welcome_root)
        self.city_entry.pack()

        self.country_label = tk.Label(welcome_root, text="Enter your country:")
        self.country_label.pack()
        self.country_entry = tk.Entry(welcome_root)
        self.country_entry.pack()

        self.phone_label = tk.Label(welcome_root, text="Enter your phone number:")
        self.phone_label.pack()
        self.phone_entry = tk.Entry(welcome_root)
        self.phone_entry.pack()

        self.email_label = tk.Label(welcome_root, text="Enter your email address:")
        self.email_label.pack()
        self.email_entry = tk.Entry(welcome_root)
        self.email_entry.pack()

        # Create a button to submit the information
        self.submit_button = tk.Button(welcome_root, text="Submit", command=self.submit_info)
        self.submit_button.pack()

    def submit_info(self):
        # Get the information from the entries
        city = self.city_entry.get()
        country = self.country_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        # Print the information
        print(f"City: {city}")
        print(f"Country: {country}")
        print(f"Phone: {phone}")
        print(f"Email: {email}")

        # Create a label to display a confirmation message
        confirmation_label = tk.Label(self.master, text="Information submitted successfully!")
        confirmation_label.pack()