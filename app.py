# gui.py
"""
Simple Tkinter GUI to run scanner.py functions.
Run: python gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import scanner
import threading
import pandas as pd

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wi-Fi Scanner")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill='x', pady=(0,8))

        self.scan_btn = ttk.Button(btn_frame, text="Scan Now", command=self.scan)
        self.scan_btn.pack(side='left')

        self.export_btn = ttk.Button(btn_frame, text="Export CSV", command=self.export_csv)
        self.export_btn.pack(side='left', padx=(8,0))

        self.tree = ttk.Treeview(frm, columns=('SSID','BSSID','Signal','Security','Channel','Warning'), show='headings')
        for c in self.tree['columns']:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True)

    def scan(self):
        self.scan_btn.config(state='disabled')
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        try:
            # Use scanner.detect_and_scan but capture to DataFrame by re-running commands
            import platform
            os_name = platform.system()
            if os_name == "Windows":
                out = scanner.run_netsh()
                import parser_windows as pw
                recs = pw.parse_netsh(out)
            elif os_name == "Linux":
                out = scanner.run_nmcli()
                import parser_linux as pl
                recs = pl.parse_nmcli(out)
            else:
                recs = []
            # prepare df
            df = pd.DataFrame(recs)
            if df.empty:
                messagebox.showinfo("Scan", "No networks found or command failed.")
                return
            # normalize
            df['signal'] = df['signal'].fillna(0).astype(int)
            df['security'] = df['security'].fillna('UNKNOWN')
            df = df.sort_values('signal', ascending=False)
            # clear tree
            for row in self.tree.get_children():
                self.tree.delete(row)
            for _, r in df.iterrows():
                warn = ""
                s = r['security'].lower() if isinstance(r['security'], str) else ''
                if 'open' in s or s.strip()=='':
                    warn = 'OPEN (UNSAFE)'
                elif 'wep' in s:
                    warn = 'WEAK (WEP)'
                self.tree.insert('', 'end', values=(r.get('ssid'), r.get('bssid'), r.get('signal'), r.get('security'), r.get('channel'), warn))
        finally:
            self.scan_btn.config(state='normal')

    def export_csv(self):
        fname = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not fname:
            return
        # fetch rows
        rows = []
        for iid in self.tree.get_children():
            rows.append(self.tree.item(iid)['values'])
        if not rows:
            messagebox.showinfo("Export", "No data to export. Run a scan first.")
            return
        df = pd.DataFrame(rows, columns=self.tree['columns'])
        df.to_csv(fname, index=False)
        messagebox.showinfo("Export", f"Saved to {fname}")

if __name__ == '__main__':
    app = App()
    app.mainloop()