# utils/asn_utils.py

import requests


def get_asn_info(ip):
    """
    Dynamically fetch ASN info for a given IP address using ipinfo.io
    """
    try:
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        org = data.get("org", "")  # e.g., "AS17494 BDCOM Online Limited"

        asn_number = ""
        asn_name = ""

        if org and org.startswith("AS"):
            parts = org.split(" ", 1)
            asn_number = parts[0]
            asn_name = parts[1] if len(parts) > 1 else ""

        return {
            "asn_number": asn_number,
            "asn_name": asn_name
        }

    except Exception as e:
        print(f"[ASN Lookup Error] for IP {ip}: {e}")
        return {
            "asn_number": "",
            "asn_name": ""
        }
