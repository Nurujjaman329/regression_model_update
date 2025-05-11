import geoip2.database
from flask import Flask, jsonify, redirect, request
from rapidfuzz import process
from user_agents import parse as parse_user_agent

app = Flask(__name__)

# Load ASN DB
try:
    reader = geoip2.database.Reader('GeoLite2-ASN.mmdb')
except FileNotFoundError:
    print("GeoLite2-ASN.mmdb file not found. ASN lookup will be disabled.")
    reader = None

# Bangladesh Districts List
BANGLADESH_DISTRICTS = [
    {"en": "Bagerhat", "bn": "বাগেরহাট"},
    {"en": "Bandarban", "bn": "বান্দরবান"},
    {"en": "Barguna", "bn": "বরগুনা"},
    {"en": "Barisal", "bn": "বরিশাল"},
    {"en": "Bhola", "bn": "ভোলা"},
    {"en": "Bogra", "bn": "বগুড়া"},
    {"en": "Brahmanbaria", "bn": "ব্রাহ্মণবাড়িয়া"},
    {"en": "Chandpur", "bn": "চাঁদপুর"},
    {"en": "Chapai Nawabganj", "bn": "চাঁপাইনবাবগঞ্জ"},
    {"en": "Chattogram", "bn": "চট্টগ্রাম"},
    {"en": "Chuadanga", "bn": "চুয়াডাঙ্গা"},
    {"en": "Comilla", "bn": "কুমিল্লা"},
    {"en": "Cox's Bazar", "bn": "কক্সবাজার"},
    {"en": "Dhaka", "bn": "ঢাকা"},
    {"en": "Dinajpur", "bn": "দিনাজপুর"},
    {"en": "Faridpur", "bn": "ফরিদপুর"},
    {"en": "Feni", "bn": "ফেনী"},
    {"en": "Gaibandha", "bn": "গাইবান্ধা"},
    {"en": "Gazipur", "bn": "গাজীপুর"},
    {"en": "Gopalganj", "bn": "গোপালগঞ্জ"},
    {"en": "Habiganj", "bn": "হবিগঞ্জ"},
    {"en": "Jamalpur", "bn": "জামালপুর"},
    {"en": "Jashore", "bn": "যশোর"},
    {"en": "Jhalokathi", "bn": "ঝালকাঠি"},
    {"en": "Jhenaidah", "bn": "ঝিনাইদহ"},
    {"en": "Joypurhat", "bn": "জয়পুরহাট"},
    {"en": "Khagrachhari", "bn": "খাগড়াছড়ি"},
    {"en": "Khulna", "bn": "খুলনা"},
    {"en": "Kishoreganj", "bn": "কিশোরগঞ্জ"},
    {"en": "Kurigram", "bn": "কুড়িগ্রাম"},
    {"en": "Kushtia", "bn": "কুষ্টিয়া"},
    {"en": "Lakshmipur", "bn": "লক্ষ্মীপুর"},
    {"en": "Lalmonirhat", "bn": "লালমনিরহাট"},
    {"en": "Madaripur", "bn": "মাদারীপুর"},
    {"en": "Magura", "bn": "মাগুরা"},
    {"en": "Manikganj", "bn": "মানিকগঞ্জ"},
    {"en": "Meherpur", "bn": "মেহেরপুর"},
    {"en": "Moulvibazar", "bn": "মৌলভীবাজার"},
    {"en": "Munshiganj", "bn": "মুন্সীগঞ্জ"},
    {"en": "Mymensingh", "bn": "ময়মনসিংহ"},
    {"en": "Naogaon", "bn": "নওগাঁ"},
    {"en": "Narail", "bn": "নড়াইল"},
    {"en": "Narayanganj", "bn": "নারায়ণগঞ্জ"},
    {"en": "Narsingdi", "bn": "নরসিংদী"},
    {"en": "Natore", "bn": "নাটোর"},
    {"en": "Netrokona", "bn": "নেত্রকোনা"},
    {"en": "Nilphamari", "bn": "নীলফামারী"},
    {"en": "Noakhali", "bn": "নোয়াখালী"},
    {"en": "Pabna", "bn": "পাবনা"},
    {"en": "Panchagarh", "bn": "পঞ্চগড়"},
    {"en": "Patuakhali", "bn": "পটুয়াখালী"},
    {"en": "Pirojpur", "bn": "পিরোজপুর"},
    {"en": "Rajbari", "bn": "রাজবাড়ী"},
    {"en": "Rajshahi", "bn": "রাজশাহী"},
    {"en": "Rangamati", "bn": "রাঙ্গামাটি"},
    {"en": "Rangpur", "bn": "রংপুর"},
    {"en": "Satkhira", "bn": "সাতক্ষীরা"},
    {"en": "Shariatpur", "bn": "শরীয়তপুর"},
    {"en": "Sherpur", "bn": "শেরপুর"},
    {"en": "Sirajganj", "bn": "সিরাজগঞ্জ"},
    {"en": "Sunamganj", "bn": "সুনামগঞ্জ"},
    {"en": "Sylhet", "bn": "সিলেট"},
    {"en": "Tangail", "bn": "টাঙ্গাইল"},
    {"en": "Thakurgaon", "bn": "ঠাকুরগাঁও"}
]

def detect_language(text):
    for ch in text:
        if '০' <= ch <= '৯' or 'অ' <= ch <= 'ঔ' or 'ক' <= ch <= 'হ':
            return 'bn'
    return 'en'

def classify_district_fuzzy(address, threshold=80):
    if not address:
        return None
    language = detect_language(address)
    district_list = [d[language] for d in BANGLADESH_DISTRICTS]
    best_match = process.extractOne(address, district_list)
    if best_match and best_match[1] >= threshold:
        idx = best_match[2]
        return BANGLADESH_DISTRICTS[idx]['en']
    return None

@app.route('/')
def home():
    return "✅ Welcome to the Order Info API. Use the /order endpoint."

@app.route('/order', methods=['GET', 'POST'])
def handle_order():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_string = request.headers.get('User-Agent', '')
    ua = parse_user_agent(user_agent_string)

    # ASN Info
    if reader:
        try:
            asn_info = reader.asn(ip)
            asn = {
                'asn': asn_info.autonomous_system_number,
                'org': asn_info.autonomous_system_organization
            }
        except:
            asn = {'asn': None, 'org': 'Unknown'}
    else:
        asn = {'asn': None, 'org': 'Unavailable'}

    # Device Info
    device = {
        'is_mobile': int(ua.is_mobile),
        'is_pc': int(ua.is_pc),
        'is_tablet': int(ua.is_tablet),
        'browser': ua.browser.family,
        'os': ua.os.family,
        'device': ua.device.family
    }

    # Location Guess (Optional Address Input)
    address = request.args.get('address') or request.form.get('address', '')
    district = classify_district_fuzzy(address) if address else None

    return jsonify({
        'ip': ip,
        'user_agent': user_agent_string,
        'asn': asn,
        'device_info': device,
        'district_detected': district
    })

if __name__ == "__main__":
    app.run(debug=True)
