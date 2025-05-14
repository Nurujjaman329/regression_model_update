# utils/email_utils.py

def get_email_provider(email):
    domain = email.split('@')[-1].lower()
    if domain in ["gmail.com"]:
        return "gmail"
    elif domain in ["yahoo.com", "yahoo.com.bd"]:
        return "yahoo"
    elif domain in ["outlook.com", "hotmail.com", "live.com"]:
        return "microsoft"
    elif domain in ["icloud.com", "me.com"]:
        return "apple"
    elif domain.endswith(".edu"):
        return "educational"
    elif domain.endswith(".gov"):
        return "government"
    elif domain and '.' in domain:
        return "corporate"
    else:
        return "other"
