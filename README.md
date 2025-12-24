# Wifi-Scanner

##  Project Overview
The Wi-Fi Network Scanner is a Python-based tool that scans nearby wireless networks and displays important information such as network name (SSID), signal strength, security type, and frequency.

This project is designed for **cybersecurity and networking learning purposes**, helping users understand how wireless networks operate and how signal strength affects connectivity.


##  Objectives
- To scan and list nearby Wi-Fi networks
- To display signal strength and security details
- To help users choose the best available network
- To demonstrate basic wireless network scanning concepts


##  Technologies Used
- **Python** – Core programming language
- **subprocess / os module** – System-level Wi-Fi scanning
- **pywifi / wifi library** – Wireless network scanning
- **Tkinter (optional)** – GUI interface


##  Features
- Scans nearby Wi-Fi networks
- Displays:
  - SSID (Network Name)
  - Signal Strength (RSSI)
  - Security Type (Open / Secured)
- Console-based or GUI-based output
- Fast scanning
- User-friendly and lightweight


##  Application Flow
1. User runs the scanner
2. Tool scans available Wi-Fi networks
3. Network details are collected
4. Results are displayed on screen
S

##  Project Structure
wifi-network-scanner/
│
├── wifi_scanner.py # Main scanning script
├── gui_app.py # Optional Tkinter GUI
├── README.md # Project documentation
├── screenshots/ # Application screenshots
└── venv/ # Virtual environment