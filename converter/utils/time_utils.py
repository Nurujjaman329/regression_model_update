from datetime import datetime


def extract_time_info(order_data):
    try:
        raw_timestamp = order_data.get("createAt", "")
        if not raw_timestamp:
            return {
                "day_of_week": None,
                "day_of_month": None,
                "hour_of_day": None
            }

        dt = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        return {
            "day_of_week": dt.strftime("%A"),
            "day_of_month": dt.day,
            "hour_of_day": dt.hour
        }
    except Exception:
        return {
            "day_of_week": None,
            "day_of_month": None,
            "hour_of_day": None
        }
