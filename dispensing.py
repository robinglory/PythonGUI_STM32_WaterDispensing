import serial
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
from datetime import datetime
from mysql_connection import Database
import time
import csv
import pandas as pd
import threading

class DispensingForm(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Dispensing")
        self.geometry("600x600")

        self.arduino_port = "COM8"
        self.baud_rate = 9600
        self.arduino = None

        self.db = Database(host='localhost', user='minkhanttun', password='29112000', database='mkt')
        if self.db.connect():
            print("Database connected successfully.")
        else:
            print("Failed to connect to the database.")

        self.initialize_serial()
        self.pump_map = self.fetch_pump_map()
        self.final_colors = self.fetch_final_colors()

        self.create_widgets()
        self.start_serial_listener()

    def format_date(self, date_string):
        try:
            date_object = datetime.strptime(date_string, "%Y-%m-%d")
            return date_object.strftime("%d %B %Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return None

    def initialize_serial(self):
        try:
            self.arduino = serial.Serial(self.arduino_port, self.baud_rate, timeout=0.1)
            time.sleep(2)
            print("Serial connection established with Arduino.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Arduino: {e}")
            self.arduino = None

    def start_serial_listener(self):
        def listen():
            buffer = ""
            while True:
                try:
                    if self.arduino and self.arduino.in_waiting:
                        byte = self.arduino.read().decode(errors='replace')
                        buffer += byte
                        if '---END---' in buffer:
                            messages = buffer.split('---END---')
                            for msg in messages[:-1]:
                                self.process_serial_line(msg.strip())
                            buffer = messages[-1]
                except Exception as e:
                    self.log_message(f"Serial listener error: {e}", 'error')
                    break
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()

    def process_serial_line(self, line):
        tag = 'success'
        if '[CALIBRATION]' in line:
            tag = 'info'
        elif '[PUMP ON]' in line or '[COMMAND]' in line:
            tag = 'command'
        elif '[ERROR]' in line or '[WARNING]' in line:
            tag = 'error'
        self.log_message(line, tag)

    def fetch_pump_map(self):
        pump_map = {}
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT BaseColor, PumpNumber FROM ColorTable")
            for base_color, pump_number in cursor.fetchall():
                if pump_number == 8:
                    pump_number = 9
                elif pump_number == 9:
                    pump_number = 8
                pump_map[base_color] = pump_number
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch pump map: {e}")
        finally:
            cursor.close()
        return pump_map

    def fetch_final_colors(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT BH_ID, FinalColor FROM BOMHeading")
            self.final_color_map = {name: bh_id for bh_id, name in cursor.fetchall()}
            return list(self.final_color_map.keys())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch final colors: {e}")
            return []
        finally:
            cursor.close()

    def create_widgets(self):
        ttk.Label(self, text="Final Color").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.final_color_combobox = ttk.Combobox(self, values=self.final_colors)
        self.final_color_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.final_color_combobox.bind("<<ComboboxSelected>>", self.load_batch_number)

        ttk.Label(self, text="Batch No").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.batch_no_entry = tk.Entry(self)
        self.batch_no_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Date").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(self, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Quantity").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.dispense_button = ttk.Button(self, text="Dispense", command=self.dispense)
        self.dispense_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.show_calib_button = ttk.Button(self, text="Show Calibration", command=self.show_calibration)
        self.show_calib_button.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        self.stop_button = ttk.Button(self, text="Stop Pumps", command=self.stop_pumps)
        self.stop_button.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.log_box = scrolledtext.ScrolledText(self, height=15, wrap=tk.WORD, bg='black', fg='white', insertbackground='white')
        self.log_box.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.log_box.tag_config('error', foreground='red')
        self.log_box.tag_config('success', foreground='lightgreen')
        self.log_box.tag_config('command', foreground='yellow')
        self.log_box.tag_config('info', foreground='cyan')

        self.export_button = ttk.Button(self, text="Export to CSV & Excel", command=self.export_data)
        self.export_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(6, weight=1)

    def log_message(self, message, tag=None):
        self.log_box.configure(state='normal')
        self.log_box.insert(tk.END, message + '\n')
        if tag:
            self.log_box.tag_add(tag, f'end-{len(message)+1}c', tk.END)
        self.log_box.see(tk.END)
        self.log_box.configure(state='disabled')

    def load_batch_number(self, event):
        selected_color = self.final_color_combobox.get()
        if selected_color in self.final_color_map:
            self.batch_no_entry.delete(0, tk.END)
            self.batch_no_entry.insert(0, f"{self.final_color_map[selected_color]}")

    def fetch_base_color_percentage(self, final_color):
        try:
            cursor = self.db.connection.cursor()
            query = "SELECT BaseColor, Percentage FROM BOMDetail WHERE BH_ID = %s"
            bh_id = self.final_color_map.get(final_color)
            cursor.execute(query, (bh_id,))
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch base color details: {e}")
            return []
        finally:
            cursor.close()

    def send_to_arduino(self, data):
        try:
            if self.arduino:
                self.arduino.write(data.encode())
                self.log_message(f"[COMMAND] {data.strip()}", 'command')
                time.sleep(0.2)
        except Exception as e:
            self.log_message(f"Error communicating with Arduino: {e}", 'error')
        return None

    def show_calibration(self):
        color = self.final_color_combobox.get()
        if not color:
            messagebox.showerror("Error", "Select a color to show calibration")
            return
        base_color_details = self.fetch_base_color_percentage(color)
        for base_color, _ in base_color_details:
            pump = self.pump_map.get(base_color, -1)
            if pump != -1:
                self.send_to_arduino(f"C{pump}\n")

    def stop_pumps(self):
        self.send_to_arduino("S\n")

    def dispense(self):
        final_color = self.final_color_combobox.get()
        batch_no = self.batch_no_entry.get()
        date = self.date_entry.get()
        quantity = self.quantity_entry.get()

        if not (final_color and batch_no and date and quantity):
            messagebox.showerror("Error", "All fields are required!")
            return
        # Update quantity in the BOMHeading table
        try:
            cursor = self.db.connection.cursor()
            update_query = "UPDATE BOMHeading SET Quantity = %s WHERE BH_ID = %s"
            cursor.execute(update_query, (quantity, batch_no))
            self.db.connection.commit()
            cursor.close()
            print(f"✔ Quantity {quantity} saved to BOMHeading for BH_ID {batch_no}")
        except Exception as e:
            self.log_message(f"Database update error: {e}", 'error')

        formatted_date = self.format_date(date)
        if not formatted_date:
            return

        base_color_details = self.fetch_base_color_percentage(final_color)
        if not base_color_details:
            messagebox.showerror("Error", f"No base color data found for {final_color}")
            return

        total_quantity = float(quantity)
        command_list = []

        for base_color, percent in base_color_details:
            pump_id = self.pump_map.get(base_color, -1)
            if pump_id == -1:
                messagebox.showerror("Error", f"No pump mapping found for {base_color}")
                return
            if pump_id == 8:
                messagebox.showerror("Error", "Pump 8 is disabled")
                return
            volume = int((percent / 100) * total_quantity)
            command_list.append((pump_id, volume))

        def send_commands():
            for pump_id, volume in command_list:
                cmd = f"D{pump_id}:{volume}"
                self.send_to_arduino(cmd + "\n")
                time.sleep(1)

        thread = threading.Thread(target=send_commands)
        thread.start()

    def export_data(self):
        try:
            cursor = self.db.connection.cursor()
            # cursor.execute("SELECT BH_ID as SrNo, FinalColor, BH_ID as BatchNo, Date FROM BOMHeading")
            # heading = cursor.fetchall()
            # df_heading = pd.DataFrame(heading, columns=["SrNo", "Final Color", "Batch No", "Date"])
            # df_heading["Quantity"] = ""

            ## Export BOMHeading and BOMDetail to CSV and Excel
            ## This section assumes BOMHeading and BOMDetail tables exist in the database
            cursor.execute("SELECT BH_ID as SrNo, FinalColor, BH_ID as BatchNo, Quantity, Date FROM BOMHeading")
            heading = cursor.fetchall()
            df_heading = pd.DataFrame(heading, columns=["SrNo", "Final Color", "Batch No", "Quantity", "Date"])

            df_heading = df_heading[["SrNo", "Final Color", "Batch No", "Quantity", "Date"]]
            df_heading.to_csv(r"C:\\Users\\ASUS\\Documents\\MinKhantTun(Project)\\PythonGUI\\PythonGUI\\Dispensing Log\\DispensingHeading.csv", index=False)
            df_heading.to_excel(r"C:\\Users\\ASUS\\Documents\\MinKhantTun(Project)\\PythonGUI\\PythonGUI\\Dispensing Log\\DispensingHeading.xlsx", index=False)

            cursor.execute("SELECT DetailID as SrNo, BH_ID, BaseColor, Percentage FROM BOMDetail")
            details = cursor.fetchall()
            detail_rows = []
            for sr, bh_id, base_color, pct in details:
                final_color = next((name for name, bid in self.final_color_map.items() if bid == bh_id), "")
                detail_rows.append([sr, final_color, bh_id, base_color, f"{pct}%", self.date_entry.get()])
            df_detail = pd.DataFrame(detail_rows, columns=["SrNo", "Final Color", "Batch No", "Base Color", "Percentage", "Date"])
            df_detail.to_csv(r"C:\\Users\\ASUS\\Documents\\MinKhantTun(Project)\\PythonGUI\\PythonGUI\\Dispensing Log\\DispensingDetail.csv", index=False)
            df_detail.to_excel(r"C:\\Users\\ASUS\\Documents\\MinKhantTun(Project)\\PythonGUI\\PythonGUI\\Dispensing Log\\DispensingDetail.xlsx", index=False)

            messagebox.showinfo("Export", "Data exported to CSV and Excel successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
        finally:
            cursor.close()

    def cancel(self):
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = DispensingForm(root)
    app.mainloop()
