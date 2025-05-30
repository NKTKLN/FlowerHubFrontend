from nicegui import app, context
from app.services import get_profile as get_profile_api

def IS_MOBILE() -> bool:
    user_agent = context.client.request.headers.get('user-agent', '').lower()

    mobile_keywords = [
        "iphone", "ipod", "ipad", "android", "blackberry", "windows phone",
        "opera mini", "mobile", "silk", "fennec", "iemobile", "webos"
    ]

    return any(keyword in user_agent for keyword in mobile_keywords)

def IS_LOGGED_IN() -> bool:
    return USER_AUTH_TOKEN() is not None

def USER_AUTH_TOKEN() -> str:
    return app.storage.user.get('auth_token', None)

def IS_USER_SELLER() -> bool:
    user_data = get_profile_api(USER_AUTH_TOKEN())
    if user_data is None:
        return False
    return user_data.get('is_user_seller', False)

def IS_USER_ADMIN() -> bool:
    user_data = get_profile_api(USER_AUTH_TOKEN())
    if user_data is None:
        return False
    return user_data.get('is_user_admin', False)
