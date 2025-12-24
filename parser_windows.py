# parser_windows.py
"""
Parser for Windows `netsh wlan show networks mode=bssid` output.
Function: parse_netsh(output: str) -> list[dict]
Each dict: {'ssid','bssid','signal','security','channel'}
"""

import re

def _clean(s):
    return s.strip()

def parse_netsh(output: str):
    lines = output.splitlines()
    networks = []
    current = {}
    ssid_re = re.compile(r'^SSID\s+\d+\s+:\s+(.*)$', re.IGNORECASE)
    bssid_re = re.compile(r'^\s*BSSID\s+\d+\s+:\s+(.*)$', re.IGNORECASE)
    signal_re = re.compile(r'^\s*Signal\s+:\s*(\d+)%', re.IGNORECASE)
    auth_re = re.compile(r'^\s*Authentication\s+:\s*(.*)$', re.IGNORECASE)
    enc_re = re.compile(r'^\s*Encryption\s+:\s*(.*)$', re.IGNORECASE)
    channel_re = re.compile(r'^\s*Channel\s+:\s*(\d+)', re.IGNORECASE)

    last_ssid = None
    for line in lines:
        line = line.rstrip()
        m = ssid_re.match(line)
        if m:
            last_ssid = _clean(m.group(1))
            continue

        m = bssid_re.match(line)
        if m:
            if last_ssid is None:
                continue
            if current:
                networks.append(current)
            current = {'ssid': last_ssid, 'bssid': _clean(m.group(1)), 'signal': None, 'security': None, 'channel': None}
            continue

        m = signal_re.match(line)
        if m and current:
            try:
                current['signal'] = int(m.group(1))
            except:
                current['signal'] = None
            continue

        m = auth_re.match(line)
        if m and current:
            auth = _clean(m.group(1))
            current['security'] = auth
            continue

        m = enc_re.match(line)
        if m and current:
            enc = _clean(m.group(1))
            sec = current.get('security') or ''
            if enc and enc.lower() not in sec.lower():
                current['security'] = (sec + " / " + enc).strip()
            continue

        m = channel_re.match(line)
        if m and current:
            try:
                current['channel'] = int(m.group(1))
            except:
                current['channel'] = None
            continue

    if current:
        networks.append(current)

    # Clean results, remove duplicates by (ssid,bssid)
    seen = set()
    cleaned = []
    for rec in networks:
        key = (rec.get('ssid'), rec.get('bssid'))
        if key in seen:
            continue
        seen.add(key)
        if rec.get('signal') is None:
            rec['signal'] = 0
        if not rec.get('security'):
            rec['security'] = 'UNKNOWN'
        cleaned.append(rec)
    return cleaned

if __name__ == '__main__':
    import sys, json
    data = sys.stdin.read()
    print(json.dumps(parse_netsh(data), indent=2))
