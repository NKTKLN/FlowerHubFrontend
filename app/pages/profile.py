from nicegui import app, ui
from app.services import get_profile as get_profile_api
from app.services import get_profile_by_id as get_profile_by_id_api
from app.services import update_profile as update_profile_api
from app.services import change_password as change_password_api
from app.utils import is_valid_email
from app.utils import USER_AUTH_TOKEN, IS_LOGGED_IN
from app.components import navbar
from app.utils.sates import IS_MOBILE

@ui.page('/profile/edit')
def edit_profile():
    navbar()

    if not IS_LOGGED_IN():
        ui.navigate.to('/')
        return

    # Получаем текущий профиль пользователя
    profile_data = get_profile_api(USER_AUTH_TOKEN())
    if profile_data is None:
        ui.notify('Ошибка загрузки данных', color='red')
        ui.navigate.to('/')
        return

    address = profile_data.get('address') or {}

    with ui.column().classes('w-full p-6 gap-6 max-w-4xl mx-auto'):
        # Заголовок
        ui.label('Редактировать профиль').classes('text-2xl font-bold mb-4')

        # Основные данные
        ui.label('Основные данные').classes('text-xl font-semibold mt-6 mb-2')
        with ui.row().classes('gap-4 w-full'):
            first_name = ui.input('Имя', value=profile_data.get('first_name', '')).classes('flex-grow')
            last_name = ui.input('Фамилия', value=profile_data.get('last_name', '')).classes('flex-grow')
        email = ui.input('Почта', value=profile_data.get('email', '')).props('type=email').classes('w-full')
        display_name = ui.input('Отображаемое имя', value=profile_data.get('display_name', '')).classes('w-full')

        # Адрес
        ui.label('Адрес').classes('text-xl font-semibold mt-6 mb-2')
        with ui.grid(columns=2).classes('gap-4 w-full'):
            street = ui.input('Улица', value=address.get('street', '')).classes('col-span-2')
            city = ui.input('Город', value=address.get('city', '')).classes('w-full')
            postal_code = ui.input('Почтовый индекс', value=address.get('postal_code', '')).classes('w-full')
            country_name = ui.input('Страна', value=address.get('country_name', '')).classes('w-full')
            country_code = ui.input('Код страны (ISO)', value=address.get('country_code', '')).classes('w-full')

        # Кнопка сохранения
        with ui.row().classes('mt-6 gap-4'):
            ui.button('Сохранить изменения', on_click=lambda: handle_update()).props('color=primary')

        ui.label('Изменить пароль').classes('text-xl font-semibold mt-6 mb-2')
        new_password = ui.input('Новый пароль', password=True, placeholder='Введите новый пароль') \
            .props('type=password').classes('w-full')
        confirm_password = ui.input('Подтвердите новый пароль', password=True, placeholder='Повторите новый пароль') \
            .props('type=password').classes('w-full')

        def handle_change_password():
            new = new_password.value
            confirm = confirm_password.value

            if not new or len(new) < 6:
                ui.notify('Новый пароль должен содержать не менее 6 символов', color='red')
                return
            if new != confirm:
                ui.notify('Новые пароли не совпадают', color='red')
                return

            result = change_password_api(app.storage.user['auth_token'], new)
            if result and result.get('detail') == "Данные пользователя успешно обновлены":
                ui.notify('Пароль успешно изменён!', color='green')
                new_password.set_value('')
                confirm_password.set_value('')
            else:
                ui.notify(result.get('details', 'Ошибка при смене пароля'), color='red')

        ui.button('Сменить пароль', on_click=handle_change_password).props('color=secondary outlined').classes('mt-2 w-full sm:w-auto')

    def handle_update():
        if not is_valid_email(email.value):
            ui.notify('Введите корректный адрес электронной почты', color='red')
            return

        payload = {
            "email": email.value,
            "first_name": first_name.value,
            "last_name": last_name.value,
            "display_name": display_name.value,
            "is_user_seller": profile_data.get('is_user_seller', False),
            "address": {
                "street": street.value,
                "city": city.value,
                "postal_code": postal_code.value,
                "country_name": country_name.value,
                "country_code": country_code.value
            }
        }

        # Если все поля адреса пустые, можно отправить null вместо объекта
        if all(not v for v in payload['address'].values()):
            payload['address'] = None

        result = update_profile_api(app.storage.user['auth_token'], payload)
        if result and result.get('success'):
            ui.notify('Данные успешно обновлены!', color='green')
        else:
            error_message = result.get('error', 'Ошибка при обновлении данных')
            ui.notify(error_message, color='red')

@ui.page('/profile')
def user_profile_redirect():
    if not IS_LOGGED_IN():
        ui.navigate.to('/')
        return
    
    profile_data = get_profile_api(USER_AUTH_TOKEN())
    if profile_data is None:
        ui.navigate.to('/')
        return

    ui.navigate.to(f'/profile/{profile_data.get("id")}')

@ui.page('/profile/{user_id}')
def user_profile(user_id: str):
    navbar()

    user = get_profile_by_id_api(USER_AUTH_TOKEN(), user_id)
    if user is None or "detail" in user:
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full gap-8 max-w-4xl mx-auto' + (' p-6' if not IS_MOBILE() else '')):
        with ui.row().classes('items-center gap-4 mb-6'):
            ui.label(user["display_name"]).classes('text-3xl font-bold')

        with ui.card().classes('w-full mb-6' + (' p-6 shadow-md' if not IS_MOBILE() else ' shadow-none')):
            ui.label('Основная информация').classes('text-xl font-semibold mb-4')

            with ui.grid(columns=2).classes('gap-x-8 gap-y-4 w-full'):
                ui.label('Имя').classes('font-medium text-gray-600')
                ui.label(user['first_name']).classes('text-lg text-gray-800')

                ui.label('Фамилия').classes('font-medium text-gray-600')
                ui.label(user['last_name']).classes('text-lg text-gray-800')

                ui.label('Email').classes('font-medium text-gray-600')
                ui.label(user['email']).classes('text-lg text-gray-800')

                ui.label('Роль').classes('font-medium text-gray-600')
                role_text = "Продавец" if user['is_user_seller'] else "Покупатель"
                ui.label(role_text).classes('text-lg text-green-600 font-semibold')

        with ui.card().classes('w-full' + (' p-6 shadow-md' if not IS_MOBILE() else ' shadow-none')):
            ui.label('Адрес').classes('text-xl font-semibold mb-4')

            address = user.get('address') or {}
            address_str = f"{address.get('street', '')}, {address.get('city', '')}, " \
                          f"{address.get('postal_code', '')}, {address.get('country_name', '')}"

            ui.label(address_str).classes('text-gray-700 leading-relaxed')

        with ui.row().classes('justify-start w-full'):
            if IS_LOGGED_IN():
                user = get_profile_api(USER_AUTH_TOKEN())
                if user is not None and str(user.get("id")) == user_id:
                    ui.button('Редактировать профиль', on_click=lambda: ui.navigate.to(f'/profile/edit')).props('color=primary')
            
            if user['is_user_seller']:
                ui.button('Посмотреть товары', on_click=lambda: ui.navigate.to(f'/?seller_id={user_id}')).props('color=primary')
