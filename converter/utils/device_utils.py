from user_agents import parse


def get_device_info(user_agent_str):
    ua = parse(user_agent_str)
    return {
        "user_browser": ua.browser.family,
        "user_os_name": ua.os.family,
        "user_device_type": "Mobile" if ua.is_mobile else "PC" if ua.is_pc else "Other",
        "user_agent": user_agent_str
    }
