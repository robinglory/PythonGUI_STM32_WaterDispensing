import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
from threading import Thread, Event
import queue
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
import os

class PumpControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pump Control System")
        self.root.geometry("1200x800")
        self.serial_connection = None
        self.serial_thread = None
        self.serial_event = Event()
        self.data_queue = queue.Queue()
        self.calibration_factors = [264.3, 10.62, 80, 38, 1, 4, 1, 1, 1]
        self.current_pump = 1
        self.history = []
        self.setup_ui()
        self.load_calibration()
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Pump Control", padding="10")
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Right panel - Log/Graph
        display_frame = ttk.LabelFrame(main_frame, text="System Output", padding="10")
        display_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        # Control Panel Widgets
        ttk.Label(control_frame, text="Serial Port:").grid(row=0, column=0, sticky="w")
        self.port_combobox = ttk.Combobox(control_frame, values=self.get_serial_ports())
        self.port_combobox.grid(row=0, column=1, sticky="ew", pady=5)
        if self.port_combobox['values']:
            self.port_combobox.current(0)
        
        self.connect_btn = ttk.Button(control_frame, text="Connect", command=self.toggle_serial)
        self.connect_btn.grid(row=0, column=2, padx=5)
        
        ttk.Label(control_frame, text="Pump Selection:").grid(row=1, column=0, sticky="w")
        self.pump_combobox = ttk.Combobox(control_frame, values=[f"Pump {i+1}" for i in range(9)])
        self.pump_combobox.current(0)
        self.pump_combobox.grid(row=1, column=1, sticky="ew", pady=5)
        self.pump_combobox.bind("<<ComboboxSelected>>", self.update_pump_selection)
        
        ttk.Label(control_frame, text="Volume (mL):").grid(row=2, column=0, sticky="w")
        self.volume_entry = ttk.Entry(control_frame)
        self.volume_entry.grid(row=2, column=1, sticky="ew", pady=5)
        self.volume_entry.insert(0, "100")
        
        ttk.Label(control_frame, text="Calibration Factor:").grid(row=3, column=0, sticky="w")
        self.calibration_entry = ttk.Entry(control_frame)
        self.calibration_entry.grid(row=3, column=1, sticky="ew", pady=5)
        self.update_calibration_display()
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Start Pump", command=self.start_pump)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop All", command=self.stop_pumps)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.calibrate_btn = ttk.Button(button_frame, text="Update Calibration", command=self.update_calibration)
        self.calibrate_btn.pack(side=tk.LEFT, padx=5)
        
        # Status indicators
        self.status_label = ttk.Label(control_frame, text="Status: Disconnected", style='Header.TLabel')
        self.status_label.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.pump_status_label = ttk.Label(control_frame, text="Pump: Idle")
        self.pump_status_label.grid(row=6, column=0, columnspan=3, sticky="w")
        
        # Display Panel Widgets
        self.log_text = scrolledtext.ScrolledText(display_frame, width=60, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Graph area
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # History button
        ttk.Button(display_frame, text="Show History", command=self.show_history).pack(pady=5)
        
    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def toggle_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        port = self.port_combobox.get()
        if not port:
            messagebox.showerror("Error", "Please select a serial port")
            return
        
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            self.serial_event.clear()
            self.serial_thread = Thread(target=self.read_serial_data)
            self.serial_thread.daemon = True
            self.serial_thread.start()
            
            self.connect_btn.config(text="Disconnect")
            self.status_label.config(text="Status: Connected")
            self.log_message(f"Connected to {port}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
    
    def disconnect_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_event.set()
            self.serial_connection.close()
            if self.serial_thread and self.serial_thread.is_alive():
                self.serial_thread.join()
            
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Status: Disconnected")
            self.log_message("Disconnected from serial port")
    
    def read_serial_data(self):
        while not self.serial_event.is_set():
            if self.serial_connection.in_waiting:
                try:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        self.data_queue.put(line)
                        self.root.after(10, self.process_serial_data)
                except UnicodeDecodeError:
                    continue
            time.sleep(0.01)
    
    def process_serial_data(self):
        while not self.data_queue.empty():
            line = self.data_queue.get()
            self.log_message(line)
            
            # Parse pump status messages
            if "Pump" in line and ("ON" in line or "OFF" in line):
                self.pump_status_label.config(text=f"Pump: {line.split('-')[0].strip()}")
            
            # Parse flow data
            if "Flow:" in line and "Total:" in line:
                try:
                    parts = line.split('|')
                    flow_rate = float(parts[0].split(':')[1].strip().split()[0])
                    total = float(parts[1].split(':')[1].strip().split()[0])
                    target = float(parts[1].split('Target:')[1].strip().split()[0][:-1])
                    
                    self.update_graph(flow_rate, total, target)
                    
                    # Save to history
                    self.history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'pump': self.current_pump,
                        'flow_rate': flow_rate,
                        'total': total,
                        'target': target,
                        'calibration': self.calibration_factors[self.current_pump-1]
                    })
                    
                except Exception as e:
                    self.log_message(f"Error parsing data: {str(e)}")
    
    def update_graph(self, flow_rate, total, target):
        self.ax.clear()
        
        # Plot flow rate
        self.ax.bar(['Flow Rate'], [flow_rate], color='skyblue')
        self.ax.set_ylabel('mL/s')
        self.ax.set_title(f'Pump {self.current_pump} - Flow Rate')
        
        # Add text annotations
        self.ax.text(0, flow_rate/2, f"{flow_rate:.2f} mL/s", ha='center', va='center')
        
        # Second axis for total and target
        ax2 = self.ax.twinx()
        ax2.plot(['Volume'], [total], 'go', markersize=10, label='Current')
        ax2.plot(['Volume'], [target], 'ro', markersize=10, label='Target')
        ax2.set_ylabel('mL')
        ax2.legend(loc='upper right')
        
        self.canvas.draw()
    
    def start_pump(self):
        if not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Error", "Not connected to serial port")
            return
        
        try:
            volume = float(self.volume_entry.get())
            if volume <= 0:
                raise ValueError("Volume must be positive")
            
            pump_num = self.pump_combobox.current() + 1
            command = f"D{pump_num}:{volume}"
            self.serial_connection.write((command + "\n").encode())
            self.current_pump = pump_num
            self.log_message(f"Sent command: {command}")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
    
    def stop_pumps(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(b"S\n")
            self.log_message("Sent stop command")
    
    def update_pump_selection(self, event=None):
        pump_num = self.pump_combobox.current() + 1
        self.update_calibration_display()
    
    def update_calibration_display(self):
        pump_num = self.pump_combobox.current() + 1
        self.calibration_entry.delete(0, tk.END)
        self.calibration_entry.insert(0, f"{self.calibration_factors[pump_num-1]:.2f}")
    
    def update_calibration(self):
        try:
            new_cal = float(self.calibration_entry.get())
            if new_cal <= 0.5:
                raise ValueError("Calibration factor must be greater than 0.5")
            
            pump_num = self.pump_combobox.current() + 1
            self.calibration_factors[pump_num-1] = new_cal
            self.save_calibration()
            
            if self.serial_connection and self.serial_connection.is_open:
                command = f"D{pump_num}:0:{new_cal}"
                self.serial_connection.write((command + "\n").encode())
                self.log_message(f"Updated calibration for Pump {pump_num} to {new_cal:.2f}")
            
            messagebox.showinfo("Success", f"Calibration for Pump {pump_num} updated to {new_cal:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def save_calibration(self):
        with open('calibration.json', 'w') as f:
            json.dump(self.calibration_factors, f)
    
    def load_calibration(self):
        if os.path.exists('calibration.json'):
            try:
                with open('calibration.json', 'r') as f:
                    loaded = json.load(f)
                    if len(loaded) == len(self.calibration_factors):
                        self.calibration_factors = loaded
            except Exception as e:
                self.log_message(f"Error loading calibration: {str(e)}")
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Pump History")
        history_window.geometry("800x600")
        
        tree = ttk.Treeview(history_window, columns=('Timestamp', 'Pump', 'Flow Rate', 'Total', 'Target', 'Calibration'), show='headings')
        tree.heading('Timestamp', text='Timestamp')
        tree.heading('Pump', text='Pump')
        tree.heading('Flow Rate', text='Flow Rate (mL/s)')
        tree.heading('Total', text='Total (mL)')
        tree.heading('Target', text='Target (mL)')
        tree.heading('Calibration', text='Calibration')
        
        tree.column('Timestamp', width=150)
        tree.column('Pump', width=50)
        tree.column('Flow Rate', width=100)
        tree.column('Total', width=100)
        tree.column('Target', width=100)
        tree.column('Calibration', width=100)
        
        for record in reversed(self.history[-100:]):  # Show last 100 records
            tree.insert('', 'end', values=(
                record['timestamp'],
                record['pump'],
                f"{record['flow_rate']:.2f}",
                f"{record['total']:.1f}",
                f"{record['target']:.1f}",
                f"{record['calibration']:.2f}"
            ))
        
        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Export button
        ttk.Button(history_window, text="Export to CSV", command=lambda: self.export_history()).pack(pady=5)
    
    def export_history(self):
        try:
            filename = f"pump_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w') as f:
                f.write("Timestamp,Pump,Flow Rate (mL/s),Total (mL),Target (mL),Calibration\n")
                for record in self.history:
                    f.write(f"{record['timestamp']},{record['pump']},{record['flow_rate']:.2f},{record['total']:.1f},{record['target']:.1f},{record['calibration']:.2f}\n")
            messagebox.showinfo("Success", f"History exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def on_closing(self):
        self.disconnect_serial()
        self.save_calibration()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PumpControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()