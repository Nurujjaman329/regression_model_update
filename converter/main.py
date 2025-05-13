import json
from datetime import datetime

# Ensure the correct imports are made
from utils.asn_utils import get_asn_info
from utils.device_utils import get_device_info
from utils.location_utils import get_location_info
from utils.phone_utils import get_operator_from_prefix  # ✅ added
from utils.time_utils import extract_time_info

# Load JSON data
with open("json_data.json") as f:
    raw_data = json.load(f)

# Define min and max for normalization
MIN_ORDER_TOTAL = 100
MAX_ORDER_TOTAL = 50000
MIN_CART_ITEM_COUNT = 1
MAX_CART_ITEM_COUNT = 10

# Function to normalize order_total
def normalize_order_total(order_total):
    return (order_total - MIN_ORDER_TOTAL) / (MAX_ORDER_TOTAL - MIN_ORDER_TOTAL)

# Function to normalize cart_item_count
def normalize_cart_item_count(cart_item_count):
    return (cart_item_count - MIN_CART_ITEM_COUNT) / (MAX_CART_ITEM_COUNT - MIN_CART_ITEM_COUNT)

# Process each order
for order in raw_data["data"]:
    # Basic fields
    order_total = order["amount"]["total"]
    cart_item_count = len(order["cart"])
    product_type = order["cart"][0]["product"]["product"]["type"] if order["cart"] else None

    # Time breakdown
    created_at = datetime.fromisoformat(order["createAt"].replace("Z", "+00:00"))
    day_of_week = created_at.strftime("%A")
    day_of_month = created_at.day
    hour_of_day = created_at.hour

    # Phone prefix & operator
    phone = order["customer"]["phone"]
    local_phone = phone[3:] if phone.startswith("+88") else phone
    phone_prefix = local_phone[:5]
    operator_name = get_operator_from_prefix(phone_prefix)

    # Enrich with utilities
    asn_info = get_asn_info(order["customerIpAddress"])
    device_info = get_device_info(order["customerUserAgent"])
    location_info = get_location_info(order.get("shippingAddress", {}))
    time_info = extract_time_info(order)

    # Normalize the order total and cart item count
    order_total_stnd = normalize_order_total(order_total)
    cart_item_count_stnd = normalize_cart_item_count(cart_item_count)

    # Combine everything
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
        "sim_operator": operator_name,  # ✅ added
        "is_coupon_used": False,
        "merchant_return_rate": 0,
        "merchant_order_count": 0,
        **asn_info,
        **device_info,
        **location_info,
        **time_info
    }

    # Print enriched order data in a readable format
    print(json.dumps(enriched, indent=2))
