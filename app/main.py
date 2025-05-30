from nicegui import ui
from app.pages import home, login, register, edit_profile, user_profile, add_flower, reference_list, cart_page, orders_page, order_detail_page, admin_users

ui.run(storage_secret="womp womp")
