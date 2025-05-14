import json
from datetime import datetime

# Utility imports
from utils.asn_utils import get_asn_info
from utils.device_utils import get_device_info
from utils.email_utils import get_email_provider  # ✅ NEW IMPORT
from utils.location_utils import get_location_info
from utils.phone_utils import get_operator_from_prefix
from utils.time_utils import extract_time_info

# Load JSON data
with open("json_data.json") as f:
    raw_data = json.load(f)

# Normalization constants
MIN_ORDER_TOTAL = 100
MAX_ORDER_TOTAL = 50000
MIN_CART_ITEM_COUNT = 1
MAX_CART_ITEM_COUNT = 10

def normalize_order_total(order_total):
    return (order_total - MIN_ORDER_TOTAL) / (MAX_ORDER_TOTAL - MIN_ORDER_TOTAL)

def normalize_cart_item_count(cart_item_count):
    return (cart_item_count - MIN_CART_ITEM_COUNT) / (MAX_CART_ITEM_COUNT - MIN_CART_ITEM_COUNT)

# Process each order
for order in raw_data["data"]:
    order_total = order["amount"]["total"]
    cart_item_count = len(order["cart"])
    product_type = order["cart"][0]["product"]["product"]["type"] if order["cart"] else None

    created_at = datetime.fromisoformat(order["createAt"].replace("Z", "+00:00"))
    day_of_week = created_at.strftime("%A")
    day_of_month = created_at.day
    hour_of_day = created_at.hour

    # Phone processing
    phone = order["customer"]["phone"]
    local_phone = phone[3:] if phone.startswith("+88") else phone
    phone_prefix = local_phone[:5]
    operator_name = get_operator_from_prefix(phone_prefix)

    # Email provider detection
    email = order["customer"].get("email", "")
    email_provider = get_email_provider(email)

    # Enrich with utilities
    asn_info = get_asn_info(order["customerIpAddress"])
    device_info = get_device_info(order["customerUserAgent"])
    location_info = get_location_info(order.get("shippingAddress", {}))
    time_info = extract_time_info(order)

    order_total_stnd = normalize_order_total(order_total)
    cart_item_count_stnd = normalize_cart_item_count(cart_item_count)

    enriched = {
        "order_total": order_total,
        "order_total_stnd": order_total_stnd,
        "cart_item_count": cart_item_count,
        "cart_item_count_stnd": cart_item_count_stnd,
        "product_type": product_type,
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "hour_of_day": hour_of_day,
        "phone_number_prefix": phone_prefix,
        "sim_operator": operator_name,
        "email_provider": email_provider,  # ✅ added
        "is_coupon_used": False,
        "merchant_return_rate": 0,
        "merchant_order_count": 0,
        **asn_info,
        **device_info,
        **location_info,
        **time_info
    }

    print(json.dumps(enriched, indent=2))
