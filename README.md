*** Run Command - > python app.py

Endpoint like this : 

/order?address=YourAddress

Example : 

http://127.0.0.1:5000/order?address=Dhaka


# 🛰️ IP Info & District Detection API (Flask)

A lightweight Flask API that provides information about the user's IP address, device, browser, ISP (ASN), and detects the most likely district in Bangladesh from an address using fuzzy matching.

---

## 🚀 Features

- Detects client **IP address** and **user-agent**.
- Parses **device type**, **OS**, and **browser**.
- Fetches **ASN (ISP info)** using MaxMind's GeoLite2-ASN database.
- Fuzzy-matches **Bangladesh district** from a given address (supports English and Bengali).
- JSON API response.

---

## 📦 Setup & Run

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <project-folder>


