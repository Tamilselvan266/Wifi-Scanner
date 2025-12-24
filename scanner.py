# scanner.py
"""
Main scanner script.
Usage:
    python scanner.py            # auto-detect OS and scan
    python scanner.py --csv out.csv   # save results to CSV
"""

import platform
import subprocess
import argparse
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import sys

def run_netsh():
    # Windows netsh command
    try:
        proc = subprocess.run(["netsh", "wlan", "show", "networks", "mode=bssid"], capture_output=True, text=True, check=True)
        return proc.stdout
    except subprocess.CalledProcessError as e:
        print("Error running netsh:", e)
        return ""

def run_nmcli():
    # Linux nmcli: produce colon-separated values for easier parsing
    # Using -t (terse) ensures one record per line
    cmd = ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,BSSID,CHAN", "device", "wifi", "list"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return proc.stdout
    except subprocess.CalledProcessError as e:
        print("Error running nmcli:", e)
        return ""

def score_security(sec_text):
    s = (sec_text or "").lower()
    if "wpa3" in s:
        return 4
    if "wpa2" in s or "wpa" in s:
        return 3
    if "wep" in s:
        return 1
    if "unknown" in s:
        return 2
    if "open" in s or s.strip() == "":
        return 0
    return 2

def label_security(sec_text):
    s = (sec_text or "").strip()
    if not s or s.lower() == 'unknown':
        return 'UNKNOWN'
    return s

def parse_and_display(records, save_csv=None):
    if not records:
        print("No networks found.")
        return
    # normalize fields and create DataFrame
    for r in records:
        r['signal'] = int(r.get('signal') or 0)
        r['security_label'] = label_security(r.get('security'))
        r['security_score'] = score_security(r.get('security'))
        r['warning'] = ''
        if r['security_score'] == 0:
            r['warning'] = 'OPEN (UNSAFE)'
        elif r['security_score'] <= 1:
            r['warning'] = 'WEAK (WEP/OLD)'
    df = pd.DataFrame(records)
    # sort by signal desc
    df = df.sort_values(by='signal', ascending=False).reset_index(drop=True)
    display_df = df[['ssid','bssid','signal','security_label','channel','warning']]
    display_df.rename(columns={
        'ssid':'SSID','bssid':'BSSID','signal':'Signal(%)','security_label':'Security','channel':'Channel','warning':'Warning'
    }, inplace=True)
    print()
    print("Scan time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Networks found:", len(display_df))
    print()
    print(tabulate(display_df, headers='keys', tablefmt='psql', showindex=True))
    if save_csv:
        display_df.to_csv(save_csv, index=False)
        print(f"\nSaved results to {save_csv}")

def detect_and_scan(save_csv=None):
    os_name = platform.system()
    if os_name == "Windows":
        print("Detected Windows OS — using netsh")
        out = run_netsh()
        if not out:
            print("netsh returned empty output. Ensure Wi-Fi is enabled and you have permission.")
            return
        import parser_windows as pw
        recs = pw.parse_netsh(out)
        parse_and_display(recs, save_csv)
    elif os_name == "Linux":
        print("Detected Linux OS — using nmcli")
        out = run_nmcli()
        if not out:
            print("nmcli returned empty output. Ensure NetworkManager is installed and you have permission.")
            return
        import parser_linux as pl
        recs = pl.parse_nmcli(out)
        parse_and_display(recs, save_csv)
    else:
        print(f"Unsupported OS: {os_name}. This tool supports Windows and Linux.")

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Wi-Fi Network Scanner (Windows & Linux)")
    ap.add_argument("--csv", help="Save scan results to CSV file")
    args = ap.parse_args()
    detect_and_scan(save_csv=args.csv)
