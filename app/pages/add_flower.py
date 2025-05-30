from nicegui import app, ui
from app.services import seller_add_flower as seller_add_flower_api
from app.services import admin_add_flower as admin_add_flower_api
from app.services import reference as ref_api
from app.services import get_profile as get_profile_api
from app.services import get_flower_data, seller_edit_flower
from app.utils import USER_AUTH_TOKEN, IS_LOGGED_IN, IS_USER_SELLER, IS_USER_ADMIN  
from app.components import navbar, load_reference_data

@ui.page('/flowers/add')
def add_flower():
    navbar()

    if not IS_LOGGED_IN() or not (IS_USER_SELLER() or IS_USER_ADMIN()):
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-6 max-w-4xl mx-auto'):
        ui.label('Добавить цветок').classes('text-2xl font-bold mb-4')

        name = ui.input('Название цветка').classes('w-full mb-4')
        variety = ui.input('Сорт (вариант)').classes('w-full mb-4')
        price = ui.input('Цена', value='0').props('type=number').classes('w-full mb-4')
        if IS_USER_ADMIN():
            seller_id = ui.input('ID Поставщика').props('type=number').classes('w-full mb-4')

        type_id, usage_id, season_id, country_id = load_reference_data()

        def handle_add():
            payload = {
                "name": name.value,
                "type_id": type_id.value,
                "usage_id": usage_id.value,
                "season_id": season_id.value,
                "country_id": country_id.value,
                "variety": variety.value,
                "price": float(price.value)
            }

            if IS_USER_ADMIN():
                result = admin_add_flower_api(USER_AUTH_TOKEN(), payload, seller_id)
            else:
                result = seller_add_flower_api(USER_AUTH_TOKEN(), payload)
           
            if result and result.get('name') == name.value:
                ui.notify('Цветок успешно добавлен!', color='green')
            else:
                error_message = result.get('detail', 'Ошибка при добавлении')
                ui.notify(error_message, color='red')

        user = get_profile_api(USER_AUTH_TOKEN())
        with ui.row().classes('justify-start w-full'):
            ui.button('Добавить цветок', on_click=handle_add).props('color=primary').classes('mt-4 w-full sm:w-auto')
            ui.button('Посмотреть товары', on_click=lambda: ui.navigate.to(f'/?seller_id={user["id"]}')).props('color=primary').classes('mt-4 w-full sm:w-auto')


@ui.page('/flower/{flower_id}/edit')
def edit_flower_page(flower_id: str):
    navbar()

    if not IS_LOGGED_IN() or not (IS_USER_SELLER() or IS_USER_ADMIN()):
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-6 max-w-4xl mx-auto'):
        ui.label('Редактировать цветок').classes('text-2xl font-bold mb-4')

        flower = None
        try:
            flowers = get_flower_data(flower_id=flower_id)
            if flowers:
                flower = flowers[0]
            else:
                ui.notify('Цветок не найден', color='red')
                ui.button('Назад', on_click=lambda: ui.navigate.back()).props('color=primary')
                return
        except Exception as e:
            ui.notify(f'Ошибка загрузки данных: {e}', color='red')
            return

        name = ui.input('Название цветка', value=flower['name']).classes('w-full mb-4')
        variety = ui.input('Сорт (вариант)', value=flower.get('variety', '')).classes('w-full mb-4')
        price = ui.input('Цена', value=str(flower['price'])).props('type=number').classes('w-full mb-4')

        type_id, usage_id, season_id, country_id = load_reference_data(
            initial_type=flower['type_id'],
            initial_usage=flower['usage_id'],
            initial_season=flower['season_id'],
            initial_country=flower['country_id']
        )

        def handle_save():
            payload = {
                "name": name.value,
                "type_id": type_id.value,
                "usage_id": usage_id.value,
                "season_id": season_id.value,
                "country_id": country_id.value,
                "variety": variety.value,
                "price": float(price.value)
            }

            result = seller_edit_flower(USER_AUTH_TOKEN(), flower_id, payload)
            if result and result.get("name") == name.value:
                ui.notify('Цветок успешно обновлён!', color='green')
            else:
                error_message = result.get('detail', 'Ошибка при сохранении')
                ui.notify(error_message, color='red')

        user = get_profile_api(USER_AUTH_TOKEN())
        with ui.row().classes('justify-start w-full gap-4'):
            ui.button('Сохранить изменения', on_click=handle_save).props('color=primary').classes('mt-4')
            ui.button('Отмена', on_click=lambda: ui.navigate.to(f'/flower/{flower_id}')).props('outline').classes('mt-4')
            ui.button('Посмотреть товары', on_click=lambda: ui.navigate.to(f'/?seller_id={user["id"]}')).props('color=secondary').classes('mt-4')
