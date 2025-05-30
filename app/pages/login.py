from nicegui import app, ui
from app.utils import is_valid_email
from app.services import login as login_api
from app.utils import IS_MOBILE

@ui.page('/login')
def login():
    def handle_login():
        email_input = email.value
        password_input = password.value

        if not is_valid_email(email_input):
            ui.notify('Введите корректный адрес электронной почты', color='red')
            return

        tokens = login_api(email_input, password_input)
        if tokens.get('access_token') and tokens.get('refresh_token'):
            app.storage.user['auth_token'] = tokens['access_token']
            app.storage.user['refresh_token'] = tokens['refresh_token']
            ui.navigate.to('/')
        else:
            ui.notify(tokens.get("detail"), color='red')

    with ui.card().classes('absolute-center w-full max-w-sm p-4 bg-white rounded-lg' + (' shadow-lg' if not IS_MOBILE() else ' shadow-none')):
        ui.label('Авторизация').classes('text-xl font-semibold mb-4')
        email = ui.input('Почта').props('type=email').classes('w-full mb-4')
        password = ui.input('Пароль', password=True).props('type=password').classes('w-full mb-4')
        ui.button('Войти', on_click=handle_login).props('color=primary').classes('w-full')
        with ui.row().classes('justify-between mt-4 w-full justify-center'):
            ui.label('Нет аккаунта?').classes('text-sm text-gray-500 hover:underline cursor-pointer').on('click', lambda: ui.navigate.to('/register'))
            ui.label('Вернуться на главную').classes('text-sm text-gray-500 hover:underline cursor-pointer').on('click', lambda: ui.navigate.to('/'))
