from nicegui import ui, app
from app.utils import IS_MOBILE, IS_LOGGED_IN, IS_USER_SELLER, USER_AUTH_TOKEN, IS_USER_ADMIN
from app.services import get_profile as get_profile_api

def navbar():
    def logout():
        app.storage.user.clear()
        ui.navigate.to('/')

    def separator():
        if IS_MOBILE():
            ui.separator().props('horizontal').classes('w-20')
        else:
            ui.separator().props('vertical')

    def navigation_buttons():
        ui.button('Главная', on_click=lambda: ui.navigate.to('/')).props('flat color=white text-color=black')
        
        if IS_LOGGED_IN() and  IS_USER_SELLER():
            user = get_profile_api(USER_AUTH_TOKEN())
            ui.button('Товары', on_click=lambda: ui.navigate.to(f'/?seller_id={user["id"]}')).props('flat color=white text-color=black')

        if IS_LOGGED_IN() and (IS_USER_SELLER() or IS_USER_ADMIN()):
            separator()
            ui.button('Добавить цветок', on_click=lambda: ui.navigate.to('/flowers/add')).props('flat color=white text-color=black')
            ui.button('Справочные данные', on_click=lambda: ui.navigate.to('/reference/list')).props('flat color=white text-color=black')
            ui.button('Заказы пользователей', on_click=lambda: ui.navigate.to('/seller/orders')).props('flat color=white text-color=black')

        if IS_LOGGED_IN() and IS_USER_ADMIN():
            separator()
            ui.button('Список пользователей', on_click=lambda: ui.navigate.to('/users')).props('flat color=white text-color=black')

        if IS_LOGGED_IN() and not IS_USER_SELLER() and not IS_USER_ADMIN():
            separator()
            ui.button('Корзина', on_click=lambda: ui.navigate.to('/cart')).props('flat color=white text-color=black')
            ui.button('Заказы', on_click=lambda: ui.navigate.to('/orders')).props('flat color=white text-color=black')

        separator()
        if IS_LOGGED_IN():
            ui.button('Профиль', on_click=lambda: ui.navigate.to('/profile')).props('flat color=white text-color=black')
            ui.button('Выход', on_click=logout).props('flat color=white text-color=black')
        else:
            ui.button('Зарегистрироваться', on_click=lambda: ui.navigate.to('/register')).props('flat color=white text-color=black')
            ui.button('Авторизоваться', on_click=lambda: ui.navigate.to('/login')).props('flat color=white text-color=black')


    with ui.header().classes('w-full px-4 py-2 bg-white shadow-md flex items-center justify-between'):
        with ui.row().classes('flex items-center gap-4'):
            ui.label('FlowerHub').classes('text-lg font-bold text-black')
        
        if not IS_MOBILE():
            with ui.row().classes('gap-4 flex justify-center flex-grow'):
                navigation_buttons()
            return 

        with ui.dialog().props('maximized persistent') as menu_dialog, ui.card().classes('w-full h-full bg-white'):
            with ui.row().classes('w-full justify-end p-4'):
                ui.button(icon='close', on_click=menu_dialog.close).props('flat color=black')
            with ui.column().classes('items-center justify-center gap-4 w-full h-full'):
                ui.label('Навигация').classes('text-lg font-bold mb-4')
                navigation_buttons()

        ui.button(on_click=menu_dialog.open, icon='menu').props('flat color=black')
