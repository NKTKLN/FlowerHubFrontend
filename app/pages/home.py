from nicegui import ui, app
from app.components import navbar
from app.services import get_flower_data, reference, get_profile_by_id, get_profile, delete_flower, update_cart
from fastapi import Request

from app.utils.sates import IS_MOBILE, IS_USER_SELLER, IS_LOGGED_IN, USER_AUTH_TOKEN, IS_USER_ADMIN


def render_filters():
    with ui.card().classes('w-full p-4 gap-4' + ('' if not IS_MOBILE() else ' shadow-none')):
        ui.label('Фильтры').classes('text-xl font-bold mb-4')

        name = ui.input('Название', value=app.storage.request.get('name', '')).classes('w-full')
        type_options = {t['id']: t['name'] for t in reference.get_types()}
        usage_options = {u['id']: u['name'] for u in reference.get_usages()}
        season_options = {s['id']: s['name'] for s in reference.get_seasons()}
        country_options = {c['id']: c['name'] for c in reference.get_countries()}

        type_id = ui.select(label='Тип', options=type_options, value=app.storage.request.get('type_id')).classes('w-full')
        usage_id = ui.select(label='Место посадки', options=usage_options, value=app.storage.request.get('usage_id')).classes('w-full')
        season_id = ui.select(label='Сезон', options=season_options, value=app.storage.request.get('season_id')).classes('w-full')
        country_id = ui.select(label='Страна', options=country_options, value=app.storage.request.get('country_id')).classes('w-full')
        min_price = ui.input('Минимальная цена', value=app.storage.request.get('min_price', '0')).props('type=number').classes('w-full')
        max_price = ui.input('Максимальная цена', value=app.storage.request.get('max_price', '1000')).props('type=number').classes('w-full')
        
        def apply_filters():
            app.storage.request.update({
                'name': name.value,
                'type_id': type_id.value,
                'usage_id': usage_id.value,
                'season_id': season_id.value,
                'country_id': country_id.value,
                'min_price': min_price.value,
                'max_price': max_price.value,
            })
            params = {k: v for k, v in app.storage.request.items() if v not in (None, '')}
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            ui.navigate.to(f'/?{query_string}')

        def clear_filters():
            app.storage.request.update({
                'name': '',
                'type_id': None,
                'usage_id': None,
                'season_id': None,
                'country_id': None,
                'min_price': '0',
                'max_price': '1000',
            })
            name.set_value('')
            type_id.set_value(None)
            usage_id.set_value(None)
            season_id.set_value(None)
            country_id.set_value(None)
            min_price.set_value('0')
            max_price.set_value('1000')

            ui.navigate.to('/')

        with ui.row().classes('w-full justify-between mt-4 gap-4'):
            ui.button('Применить фильтры', on_click=apply_filters).props('color=primary').classes('flex-grow')
            ui.button('Очистить фильтры', on_click=clear_filters).props('outline color=grey').classes('flex-grow')

def render_flower_card(flower):
    with ui.card().classes('w-full shadow-md hover:shadow-lg transition-shadow'):
        with ui.row().classes('w-full justify-between items-center px-4 py-4'):
            with ui.link(target=f'/flower/{flower["id"]}').classes('flex-1 no-underline cursor-pointer'):
                with ui.column().classes('gap-1'):
                    ui.label(flower['name']).classes('text-lg text-black font-semibold')
                    if flower.get('variety'):
                        ui.label(f"Сорт: {flower['variety']}").classes('text-sm text-gray-600')
                    ui.label(f"{flower['price']} ₽").classes('text-lg font-bold text-primary')

            if IS_LOGGED_IN() and (IS_USER_SELLER() or IS_USER_ADMIN()):
                seller_ids = flower.get('seller_ids', [])
                profile = get_profile(USER_AUTH_TOKEN()) if seller_ids else None
                if (profile and profile["id"] in seller_ids) or IS_USER_ADMIN():
                    with ui.row().classes('items-center gap-2 whitespace-nowrap'):
                        def on_edit(fid):
                            ui.navigate.to(f'/flower/{fid}/edit')
         
                        def on_delete(fid):
                            def delete_handler():
                                res = delete_flower(USER_AUTH_TOKEN(), fid)
                                if res.get("detail") == "Цветок удалён успешно":
                                    ui.notify("Цветок удалён успешно", color='green')
                                else:
                                    ui.notify(res.get("detail"), color='red')

                                with flowers_container:
                                    flowers_container.clear()
                                    params = app.storage.request
                                    flowers = get_flower_data(**params)
                                    for f in flowers:
                                        render_flower_card(f)

                            with ui.dialog() as dialog, ui.card():
                                ui.label('Вы уверены, что хотите удалить этот товар?').classes('text-lg')
                                with ui.row().classes('justify-end mt-4 gap-2'):
                                    ui.button('Отмена', on_click=dialog.close).props('outline')
                                    ui.button('Удалить', on_click=lambda: [delete_handler(), dialog.close()]).props('color=red')
                            dialog.open()

                        ui.button(icon="edit", on_click=lambda e, fid=flower['id']: on_edit(fid)) \
                            .props('dense outline size=sm color=primary') \
                            .classes('whitespace-nowrap edit-btn')
                        ui.button(icon="delete", on_click=lambda e, fid=flower['id']: on_delete(fid)) \
                            .props('dense outline size=sm color=red') \
                            .classes('whitespace-nowrap delete-btn')

            if IS_LOGGED_IN() and not (IS_USER_SELLER() or IS_USER_ADMIN()):
                cart = app.storage.user.get('cart', {})
                quantity = cart.get(str(flower['id']), 0)

                def create_controls(fid):
                    with ui.row().classes('items-center gap-2 whitespace-nowrap'):
                        def on_minus():
                            cart = app.storage.user.get('cart', {})
                            current = cart.get(str(fid), 0)
                            if current > 0:
                                cart[str(fid)] = current - 1
                                app.storage.user['cart'] = cart
                                update_cart(USER_AUTH_TOKEN(), cart)
                                update_ui()

                        def on_plus():
                            cart = app.storage.user.get('cart', {})
                            current = cart.get(str(fid), 0)
                            cart[str(fid)] = current + 1
                            app.storage.user['cart'] = cart
                            update_cart(USER_AUTH_TOKEN(), cart)
                            update_ui()

                        def update_ui():
                            with flowers_container:
                                flowers_container.clear()
                                params = app.storage.request
                                flowers = get_flower_data(**params)
                                for f in flowers:
                                    render_flower_card(f)

                        if quantity > 0:
                            ui.button(icon="remove", on_click=on_minus).props('dense outline size=sm color=secondary')
                            ui.label(str(quantity)).classes('min-w-[1.5rem] text-center')
                            ui.button(icon="add", on_click=on_plus).props('dense outline size=sm color=primary')
                        else:
                            ui.button('Добавить', icon='shopping_cart', on_click=on_plus) \
                              .props('outline size=sm color=secondary') \
                              .classes('whitespace-nowrap add-btn')
                create_controls(flower['id'])

def render_pagination(current_offset, limit):
    with ui.row().classes('w-full justify-center gap-2 mt-6 flex-wrap'):
        prev_offset = max(0, current_offset - limit)
        next_offset = current_offset + limit

        def go_to(offset):
            app.storage.request['offset'] = offset
            params = {k: v for k, v in app.storage.request.items() if v not in (None, '')}
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            ui.navigate.to(f'/?{query_string}')

        ui.button('Назад', icon="arrow_back", on_click=lambda: go_to(prev_offset)).props('flat').classes('px-4 py-2')
        with ui.button(on_click=lambda: go_to(next_offset)).props('flat').classes('px-4 py-2'):
            ui.label('Вперёд')
            ui.icon('arrow_forward').classes('ml-2') 

@ui.page('/')
def home(request: Request):
    navbar()

    app.storage.request = {
        'name': request.query_params.get('name', ''),
        'type_id': int(request.query_params.get('type_id')) if request.query_params.get('type_id') else None,
        'season_id': int(request.query_params.get('season_id')) if request.query_params.get('season_id') else None,
        'usage_id': int(request.query_params.get('usage_id')) if request.query_params.get('usage_id') else None,
        'country_id': int(request.query_params.get('country_id')) if request.query_params.get('country_id') else None,
        'min_price': float(request.query_params.get('min_price')) if request.query_params.get('min_price') else None,
        'max_price': float(request.query_params.get('max_price')) if request.query_params.get('max_price') else None,
        'limit': int(request.query_params.get('limit', 25)),
        'offset': int(request.query_params.get('offset', 0)),
        'seller_id': int(request.query_params.get('seller_id')) if request.query_params.get('seller_id') else None,
    }

    with ui.dialog() as mobile_filter_dialog, ui.card().classes('w-full h-full bg-white'):
        mobile_filter_dialog.props('full-width full-height').style('margin:0; padding:0; max-width:none')

        with ui.row().classes('w-full justify-end p-4'):
            ui.button(icon='close', on_click=mobile_filter_dialog.close).props('flat color=black')

        render_filters()

    with ui.column().classes('w-full p-6 gap-6 max-w-7xl mx-auto'):
        ui.label('Цветы').classes('text-3xl font-bold mb-4 pl-4')

        with ui.row().classes('w-full flex-wrap items-start gap-6'):
            with ui.row().classes('w-full sm:hidden justify-center mb-4'):
                ui.button('Фильтры', icon='filter_alt', on_click=mobile_filter_dialog.open).props('outline color=primary')

            if not IS_MOBILE():
                with ui.column().classes('sm:flex sm:flex-col sm:w-1/5 sm:sticky sm:top-24 self-start'):
                    render_filters()

            global flowers_container
            flowers_container = ui.column().classes('w-full sm:w-3/4 gap-6')

        pagination_container = ui.column().classes('w-full mt-6')

        def load_page():
            params = app.storage.request
            flowers = get_flower_data(**params)

            flowers_container.clear()
            pagination_container.clear()

            with flowers_container:
                if flowers:
                    with ui.grid(columns=[1, 2, 3]).classes('gap-4 w-full'):
                        for flower in flowers:
                            render_flower_card(flower)
                else:
                    ui.label('Цветы не найдены').classes('text-lg text-red-500')

            with pagination_container:
                limit = params['limit']
                offset = params['offset']
                render_pagination(offset, limit)

        load_page()

@ui.page('/flower/{flower_id}')
def flower_detail_page(flower_id: str):
    navbar()

    with ui.column().classes('w-full p-6 gap-6 max-w-4xl mx-auto'):
        flowers = get_flower_data(flower_id=flower_id)
        if not flowers:
            with ui.card().classes('w-full p-6 bg-red-50 text-red-600 rounded-lg text-center'):
                ui.label('Цветок не найден').classes('text-xl font-medium')
            return
        flower = flowers[0]

        ui.label(flower['name']).classes('text-3xl font-bold text-center mb-4')

        with ui.card().classes('w-full p-6 rounded-xl bg-white' + (' shadow-lg' if not IS_MOBILE() else ' shadow-none')):
            ui.label('Характеристики:').classes('text-xl font-semibold')

            with ui.grid(columns=2).classes('gap-4 w-full mb-4'):
                ui.label('Тип:').classes('font-semibold')
                types = reference.get_types()
                type_name = next((item["name"] for item in types if item["id"] == flower['type_id']), 'Неизвестный')
                ui.label(type_name).classes('text-gray-700')

                ui.label('Место посадки:').classes('font-semibold')
                usages = reference.get_usages()
                usage_name = next((item["name"] for item in usages if item["id"] == flower['usage_id']), 'Неизвестный')
                ui.label(usage_name).classes('text-gray-700')

                ui.label('Сезон:').classes('font-semibold')
                seasons = reference.get_seasons()
                season_name = next((item["name"] for item in seasons if item["id"] == flower['season_id']), 'Неизвестный')
                ui.label(season_name).classes('text-gray-700')

                ui.label('Страна:').classes('font-semibold')
                countries = reference.get_countries()
                country_name = next((item["name"] for item in countries if item["id"] == flower['country_id']), 'Неизвестный')
                ui.label(country_name).classes('text-gray-700')

                ui.label('Сорт:').classes('font-semibold')
                ui.label(flower.get('variety') or '—').classes('text-gray-700')

                ui.label('Цена:').classes('font-semibold')
                ui.label(f"{flower['price']} ₽").classes('text-lg font-bold text-primary')

            seller_ids = flower.get('seller_ids', [])
            if seller_ids:
                ui.label('Поставщики:').classes('text-xl font-semibold mt-6')

                with ui.list().props('bordered separator').classes('w-full rounded-lg overflow-hidden'):
                    for seller_id in seller_ids:
                        try:
                            seller = get_profile_by_id("", seller_id)
                            seller_name = seller["display_name"]
                        except Exception:
                            seller_name = f'Продавец #{seller_id}'

                        with ui.item().props('dense clickable').classes('hover:bg-blue-50 transition-colors items-center'):
                            with ui.link(target=f'/profile/{seller_id}').classes('w-full no-underline flex items-center'):
                                ui.item_label(seller_name).classes('text-sm')
            else:
                with ui.card().classes('w-full p-4 rounded-lg bg-yellow-50 text-yellow-700'):
                    ui.label('Нет доступных поставщиков для этого цветка.').classes('text-sm')

            with ui.row().classes('mt-6 justify-end w-full'):
                ui.button('Назад к каталогу', on_click=lambda: ui.navigate.back()).props('outline color=primary').classes('px-4 py-2')
