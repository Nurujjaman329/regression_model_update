def get_location_info(address_data):
    return {
        "district": address_data.get("district", "Unknown")
    }
