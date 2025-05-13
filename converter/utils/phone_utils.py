# utils/phone_utils.py

def get_operator_from_prefix(prefix: str) -> str:
    if prefix.startswith("013") or prefix.startswith("017"):
        return "Grameenphone"
    elif prefix.startswith("014") or prefix.startswith("019"):
        return "Banglalink"
    elif prefix.startswith("015"):
        return "Teletalk"
    elif prefix.startswith("016"):
        return "Airtel"
    elif prefix.startswith("018"):
        return "Robi"
    else:
        return "Unknown"
