# parser_linux.py
"""
Parser for Linux `nmcli -t -f SSID,SIGNAL,SECURITY,BSSID,CHAN device wifi list` output.
Function: parse_nmcli(output: str) -> list[dict]
Each dict: {'ssid','bssid','signal','security','channel'}
"""

def parse_nmcli(output: str):
    records = []
    for raw in output.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        # nmcli -t uses colon separators. split into max 5 parts:
        # SSID:SIGNAL:SECURITY:BSSID:CHAN
        parts = raw.split(':', 4)
        # Ensure we have exactly 5 parts; if not, pad
        while len(parts) < 5:
            parts.append('')
        ssid, signal, security, bssid, chan = parts
        # Clean and convert
        try:
            signal_val = int(signal) if signal else 0
        except:
            signal_val = 0
        chan_val = None
        try:
            chan_val = int(chan) if chan else None
        except:
            chan_val = None
        rec = {
            'ssid': ssid or '<Hidden>',
            'bssid': bssid or '',
            'signal': signal_val,
            'security': security or 'UNKNOWN',
            'channel': chan_val
        }
        records.append(rec)
    return records

if __name__ == '__main__':
    import sys, json
    data = sys.stdin.read()
    print(json.dumps(parse_nmcli(data), indent=2))
