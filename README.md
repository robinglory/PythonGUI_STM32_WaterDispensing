# Color Dispensing Control Panel

🧪 **Color Dispensing Control Panel** is a modern Python GUI application designed to manage paint color dispensing operations. It integrates smoothly with an STM32-based pump control system and MySQL database for robust, precise, and user-friendly color dispensing, stock management, and bill of materials (BOM) handling.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [Serial Communication](#serial-communication)
- [Exporting Reports](#exporting-reports)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## Project Overview

This desktop application is tailored for paint dispensing workflows where color formulations (BOMs) and pump calibrations matter. It includes:

- Color Entry: Manage base colors and associate pump numbers.
- BOM Entry: Define color mixes with percentages.
- Stock Entry: Record incoming stock quantities with batch numbers and dates.
- Dispensing: Send volume commands to STM32 pumps with calibration and real-time logs.
- Export: Save stock history as CSV and Excel reports.
- Filtered stock history with date range support for auditing and inventory control.

---

## Features

- Elegant and responsive Tkinter GUI with light theme.
- Real-time serial communication with STM32 pumps.
- Dynamic calibration per pump and volume range.
- Pump ID remapping for hardware constraints (e.g., Pump 8 ↔ Pump 9).
- Stock management integrated with MySQL database.
- Date-filtered stock history log.
- Export stock reports to CSV and Excel formats.
- Multi-window layout separating dispensing and stock history views.
- User-friendly error handling and status messages.

---

## Technology Stack

- **Python 3.12**
- **Tkinter** for GUI
- **MySQL** for database management
- **PyMySQL** for Python-MySQL connectivity
- **tkcalendar** for date selection widgets
- **pandas** for CSV and Excel export
- **openpyxl** for Excel file handling
- **Serial communication** via `pyserial` (connects to STM32 firmware)

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/ColorDispensingControlPanel.git
   cd ColorDispensingControlPanel
2. Create and activate a Python virtual environment (optional but recommended):

```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
3. Install dependencies:
```
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
- Create the database mkt.

- Create required tables: ColorTable, BOMHeading, BOMDetail, StockRecord (see Database Setup section).

5. Configure database connection:

Edit the database credentials in your Python files (e.g., stockentry.py):
```
self.db = Database(host='localhost', user='your_user', password='your_password', database='mkt')
```
---------
## Database Setup
Ensure the following tables exist with the given structure (sample):
```
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
--------
## Usage
Run the main application:
```
python main.py
``` 
- Navigate through the main menu for Color Entry, BOM Entry, Stock Entry, and Dispensing.

- Use the date filters in Stock Entry to view and export stock history.

- In Dispensing, choose colors and volumes to send commands to STM32 pumps.

- Monitor calibration values and pump logs in real time.

--------

## Serial Communication
The application communicates with STM32 microcontroller via serial port (default: COM8, baud rate: 9600). Ensure:

- Correct COM port is set.

- STM32 firmware is running and responding to commands.

- Pump calibrations are synchronized with GUI settings.
---------------
## Exporting Reports
Stock history can be exported as:

- CSV: Comma-separated text format for compatibility.

- Excel (.xlsx): Well-formatted spreadsheet with dates and quantities.

Exports save automatically in the folder:

```
C:\Users\ASUS\Documents\MinKhantTun(Project)\PythonGUI\PythonGUI\Stock Entry Log
```
You can modify the folder path in stockentry.py if needed.

---------------------
## Troubleshooting
- Database Connection Error: Verify MySQL credentials and database server status.

- Serial Communication Issues: Confirm correct COM port and cable connection.

- Pump Calibration Mismatches: Re-check calibration values in Dispensing calibration menu.

- GUI Layout Problems: Ensure consistent use of geometry managers (pack or grid) in your Tkinter widgets.

- Missing Dependencies: Install required Python packages with pip install -r requirements.txt.

------------------------

## Contributing
Contributions are welcome! Please:

- Fork the repository.

- Create a feature branch (git checkout -b feature/your-feature).

- Commit your changes (git commit -m 'Add some feature').

- Push to branch (git push origin feature/your-feature).

- Open a Pull Request.

-----------------
# Credits
- Developed by Yan Naing Kyaw Tint (Robin) — Mechatronics and Computer Science student.

- Inspired by embedded systems and paint dispensing automation needs.

- Uses open source libraries: Tkinter, PyMySQL, tkcalendar, pandas, openpyxl.

License
This project is licensed under the MIT License.

