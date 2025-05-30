from nicegui import ui
from app.services import register as register_api
from app.utils import is_valid_email
from app.utils import IS_MOBILE

@ui.page('/register')
def register():
    def handle_register():
        email_input = email.value
        password_input = password.value
        first_name_input = first_name.value
        last_name_input = last_name.value
        is_seller = is_user_seller.value

        # Проверка email
        if not is_valid_email(email_input):
            ui.notify('Введите корректный адрес электронной почты', color='red')
            return

        # Проверка пароля (например, минимум 6 символов)
        if len(password_input) < 6:
            ui.notify('Пароль должен содержать не менее 6 символов', color='red')
            return

        # Проверка имени и фамилии
        if not first_name_input or not last_name_input:
            ui.notify('Введите имя и фамилию', color='red')
            return

        result = register_api(email=email_input, password=password_input, first_name=first_name_input, last_name=last_name_input, is_user_seller=is_seller)
        if result.get('access_token') and result.get('refresh_token'):
            ui.notify('Регистрация успешна!', color='green')
            ui.navigate.to('/login')
        else:
            ui.notify(result.get("detail"), color='red')

    with ui.card().classes('absolute-center w-full max-w-sm p-4 bg-white rounded-lg' + (' shadow-lg' if not IS_MOBILE() else ' shadow-none')):
        ui.label('Регистрация').classes('text-xl font-semibold mb-4')

        email = ui.input('Почта').props('type=email').classes('w-full mb-4')
        password = ui.input('Пароль', password=True).props('type=password').classes('w-full mb-4')
        first_name = ui.input('Имя').props('type=text').classes('w-full mb-4')
        last_name = ui.input('Фамилия').props('type=text').classes('w-full mb-4')
        is_user_seller = ui.checkbox('Зарегистрироваться как продавец').classes('mb-4')

        ui.button('Зарегистрироваться', on_click=handle_register).props('color=primary').classes('w-full mt-2')

        with ui.row().classes('justify-between mt-4 w-full justify-center'):
            ui.label('Уже есть аккаунт?').classes('text-sm text-gray-500 hover:underline cursor-pointer').on('click', lambda: ui.navigate.to('/login'))
            ui.label('Вернуться на главную').classes('text-sm text-gray-500 hover:underline cursor-pointer').on('click', lambda: ui.navigate.to('/'))
