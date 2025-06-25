# Color Dispensing Control Panel

🧪 **Color Dispensing Control Panel** is a modern Python GUI application designed to manage paint color dispensing operations. It integrates smoothly with an STM32-based pump control system and MySQL database for robust, precise, and user-friendly color dispensing, stock management, and bill of materials (BOM) handling.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Technology Stack](#technology-stack)
* [Prototype Demo Videos](#prototype-demo-videos) 
* [Installation](#installation)
* [Database Setup](#database-setup)
* [Usage](#usage)
* [Serial Communication](#serial-communication)
* [Exporting Reports](#exporting-reports)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [Credits](#credits)
* [License](#license)

---

## Project Overview

This desktop application is tailored for paint dispensing workflows where color formulations (BOMs) and pump calibrations matter. It includes:

* Color Entry: Manage base colors and associate pump numbers.
* BOM Entry: Define color mixes with percentages.
* Stock Entry: Record incoming stock quantities with batch numbers and dates.
* Dispensing: Send volume commands to STM32 pumps with calibration and real-time logs.
* Export: Save stock history as CSV and Excel reports.
* Filtered stock history with date range support for auditing and inventory control.
* Simulated actual dispensing volumes with ±0.5% variance and calculated differences.
* Export of dispensing logs including actual and difference volumes for each batch.

---

## Features

* Elegant and responsive Tkinter GUI with light theme.
* Real-time serial communication with STM32 pumps.
* Dynamic calibration per pump and volume range.
* Pump ID remapping for hardware constraints (e.g., Pump 8 ↔ Pump 9).
* Stock management integrated with MySQL database.
* Date-filtered stock history log.
* Export stock and dispensing reports to CSV and Excel formats.
* Simulated actual quantity and difference recording for dispensing sessions.
* Multi-window layout separating dispensing and stock history views.
* User-friendly error handling and status messages.

---

## Technology Stack

* **Python 3.12**
* **Tkinter** for GUI
* **MySQL** for database management
* **PyMySQL** for Python-MySQL connectivity
* **tkcalendar** for date selection widgets
* **pandas** for CSV and Excel export
* **openpyxl** for Excel file handling
* **Serial communication** via `pyserial` (connects to STM32 firmware)
* **random** module to simulate slight variance in actual dispensed volume

---
## Prototype Demo Videos 
---
| Feature | Preview | Watch |
|--------|---------|-------|
| **1. Color Entry** | [![Color Entry](https://img.youtube.com/vi/_TqE4AjzLSA/0.jpg)](https://youtu.be/_TqE4AjzLSA) | [Watch Video](https://youtu.be/_TqE4AjzLSA) |
| **2. BOM Entry**   | [![BOM Entry](https://img.youtube.com/vi/PpaTtH__2nQ/0.jpg)](https://youtu.be/PpaTtH__2nQ) | [Watch Video](https://youtu.be/PpaTtH__2nQ) |
| **3. Stock Entry** | [![Stock Entry](https://img.youtube.com/vi/aDptstXETww/0.jpg)](https://youtu.be/aDptstXETww) | [Watch Video](https://youtu.be/aDptstXETww) |
| **4. Dispensing System** | [![Dispensing](https://img.youtube.com/vi/LA_uo2wr364/0.jpg)](https://youtu.be/LA_uo2wr364) | [Watch Video](https://youtu.be/LA_uo2wr364) |
---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/ColorDispensingControlPanel.git
   cd ColorDispensingControlPanel
   ```

2. Create and activate a Python virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Ensure your requirements.txt includes:

   ```
   pymysql
   tkcalendar
   pandas
   openpyxl
   pyserial
   ```

4. Setup MySQL database:

   * Create the database `mkt`.
   * Create required tables: `ColorTable`, `BOMHeading`, `BOMDetail`, `StockRecord` (see Database Setup section).
   * Make sure `BOMHeading` table includes columns: `ActualQuantity` and `DifferenceQuantity` (for volume simulation).

5. Configure database connection:

   Edit the database credentials in your Python files (e.g., `stockentry.py`):

   ```python
   self.db = Database(host='localhost', user='your_user', password='your_password', database='mkt')
   ```

---

## Database Setup

Ensure the following tables exist with the given structure (sample):

```sql
CREATE TABLE ColorTable (
    ColorID VARCHAR(255) PRIMARY KEY,
    BaseColor VARCHAR(255) NOT NULL,
    PumpNumber INT NOT NULL,
    Stock INT NOT NULL,
    Date DATE NOT NULL
);

CREATE TABLE BOMHeading (
    BH_ID VARCHAR(10) PRIMARY KEY,
    FinalColor VARCHAR(255) NOT NULL,
    Quantity FLOAT DEFAULT 0,
    ActualQuantity FLOAT DEFAULT NULL,
    DifferenceQuantity FLOAT DEFAULT NULL,
    Date DATE NOT NULL
);

CREATE TABLE BOMDetail (
    DetailID INT AUTO_INCREMENT PRIMARY KEY,
    BH_ID VARCHAR(10),
    BaseColor VARCHAR(255),
    Percentage INT,
    FOREIGN KEY (BH_ID) REFERENCES BOMHeading(BH_ID)
);

CREATE TABLE StockRecord (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    ColorID VARCHAR(255) NOT NULL,
    BatchNumber VARCHAR(255) NOT NULL,
    Come INT NOT NULL,
    Date DATE NOT NULL
);
```

---

## Usage

Run the main application:

```bash
python main.py
```

* Navigate through the main menu for Color Entry, BOM Entry, Stock Entry, and Dispensing.
* Use the date filters in Stock Entry to view and export stock history.
* In Dispensing, choose colors and volumes to send commands to STM32 pumps.
* Monitor calibration values and pump logs in real time.
* Simulated actual dispensing volumes will be saved in the database with small ±0.5% variance.
* Differences between target and actual volume are recorded and exported.

---

## Serial Communication

The application communicates with STM32 microcontroller via serial port (default: COM8, baud rate: 9600). Ensure:

* Correct COM port is set.
* STM32 firmware is running and responding to commands.
* Pump calibrations are synchronized with GUI settings.
* Simulated actual volume updates occur after dispensing each batch.

---

## Exporting Reports

Stock and dispensing data can be exported as:

* **CSV**: Comma-separated text format for compatibility.
* **Excel (.xlsx)**: Well-formatted spreadsheet with dates, quantities, actual and difference values.

Exports save automatically in the folder:

```
C:\Users\ASUS\Documents\MinKhantTun(Project)\PythonGUI\PythonGUI\Stock Entry Log
```

or

```
C:\Users\ASUS\Documents\MinKhantTun(Project)\PythonGUI\PythonGUI\Dispensing Log
```

You can modify the folder path in `stockentry.py` and `dispensing.py` if needed.

---

## Troubleshooting

* **Database Connection Error**: Verify MySQL credentials and database server status.
* **Serial Communication Issues**: Confirm correct COM port and cable connection.
* **Pump Calibration Mismatches**: Re-check calibration values in Dispensing calibration menu.
* **GUI Layout Problems**: Ensure consistent use of geometry managers (pack or grid) in your Tkinter widgets.
* **Missing Dependencies**: Install required Python packages with `pip install -r requirements.txt`.
* **Export Data Missing**: Make sure dispensing has been completed at least once for each batch to store simulated values.

---

## Contributing

Contributions are welcome! Please:

* Fork the repository.
* Create a feature branch (`git checkout -b feature/your-feature`).
* Commit your changes (`git commit -m 'Add some feature'`).
* Push to branch (`git push origin feature/your-feature`).
* Open a Pull Request.

---

## Credits

* Developed by Yan Naing Kyaw Tint (Robin) — Mechatronics and Computer Science student.
* Inspired by embedded systems and paint dispensing automation needs.
* Uses open source libraries: Tkinter, PyMySQL, tkcalendar, pandas, openpyxl.
* Based on serial integration with firmware from companion repo: [stm32-water-dispense-controller](https://github.com/robinglory/stm32-water-dispense-controller)
* This GUI repository: [PythonGUI\_STM32\_WaterDispensing](https://github.com/robinglory/PythonGUI_STM32_WaterDispensing)

---

## License

This project is licensed under the MIT License.
