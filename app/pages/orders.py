import time
from nicegui import app, ui
from app.utils import USER_AUTH_TOKEN, IS_LOGGED_IN, IS_USER_SELLER, IS_MOBILE, IS_USER_ADMIN
from app.services import get_orders, get_order_by_id, get_flower_data, get_seller_orders, get_profile_by_id, get_admin_orders, update_order_status
from app.components import navbar

@ui.page('/orders')
def orders_page():
    navbar()

    if not IS_LOGGED_IN() or IS_USER_SELLER():
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-6 max-w-7xl mx-auto'):
        ui.label('Мои заказы').classes('text-3xl font-bold mb-2 text-center')

        global orders_container
        orders_container = ui.column().classes('w-full gap-6')

        def load_orders():
            data = get_orders(USER_AUTH_TOKEN())
            orders_container.clear()

            if not data:
                with orders_container:
                    ui.label('Нет оформленных заказов').classes('text-lg text-gray-500 text-center')
                return

            with orders_container:
                with ui.grid(columns=[1, 2, 3]).classes('gap-4 w-full'):
                    for order in data:
                        render_order_card(order)

        def render_order_card(order):
            with ui.card().classes('w-full hover:shadow-xl transition-shadow rounded-lg cursor-pointer' + (' shadow-md' if not IS_MOBILE() else ' shadow-none')):
                with ui.link(target=f'/order/{order["order_id"]}').classes('no-underline w-full'):
                    with ui.column().classes('p-4'):
                        with ui.row().classes('justify-between w-full items-center'):
                            ui.label(f'Заказ #{order["order_id"]}').classes('text-lg font-semibold text-primary')
                            ui.label(order['order_date']).classes('text-sm text-gray-500')
                            ui.label('Закрыт' if order['is_closed'] else 'Открыт').classes('text-sm' + (' text-red-500' if order['is_closed'] else ' text-green-500'))

                        items = order.get("items", [])
                        item_descriptions = []
                        for item in items[:3]:
                            flower_data = get_flower_data(flower_id=item['flower_id'])
                            flower_name = flower_data[0]['name'] if isinstance(flower_data, list) else flower_data.get('name', 'Неизвестный товар')
                            item_descriptions.append(f"{flower_name} ×{item['quantity']}")

                        if len(items) > 3:
                            item_descriptions.append('...')

                        ui.markdown(', '.join(item_descriptions)).classes('text-sm text-gray-600 mt-2')
                
                if IS_MOBILE():
                    ui.separator()

        load_orders()

@ui.page('/seller/orders')
def seller_orders_page():
    navbar()

    if not IS_LOGGED_IN() or not (IS_USER_SELLER() or IS_USER_ADMIN()):
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-6 max-w-7xl mx-auto'):
        ui.label('Заказы пользователей').classes('text-3xl font-bold mb-2 text-center')

        global orders_container
        orders_container = ui.column().classes('w-full gap-6')

        def load_orders():
            if IS_USER_SELLER():
                data = get_seller_orders(USER_AUTH_TOKEN())
            elif IS_USER_ADMIN():
                data = get_admin_orders(USER_AUTH_TOKEN())
            orders_container.clear()

            if not data:
                with orders_container:
                    ui.label('Нет оформленных заказов').classes('text-lg text-gray-500 text-center')
                return

            with orders_container:
                with ui.grid(columns=[1, 2, 3]).classes('gap-4 w-full'):
                    for order in data:
                        render_order_card(order)

        def render_order_card(order):
            with ui.card().classes('w-full hover:shadow-xl transition-shadow rounded-lg cursor-pointer' + (' shadow-md' if not IS_MOBILE() else ' shadow-none')):
                with ui.link(target=f'/order/{order["order_id"]}').classes('no-underline w-full'):
                    with ui.column().classes('p-4'):
                        with ui.row().classes('justify-between w-full items-center'):
                            ui.label(f'Заказ #{order["order_id"]}').classes('text-lg font-semibold text-primary')
                            ui.label(order['order_date']).classes('text-sm text-gray-500')
                            ui.label('Закрыт' if order['is_closed'] else 'Открыт').classes('text-sm' + (' text-red-500' if order['is_closed'] else ' text-green-500'))

                        items = order.get("items", [])
                        item_descriptions = []
                        for item in items[:3]:
                            flower_data = get_flower_data(flower_id=item['flower_id'])
                            flower_name = flower_data[0]['name'] if isinstance(flower_data, list) else flower_data.get('name', 'Неизвестный товар')
                            item_descriptions.append(f"{flower_name} ×{item['quantity']}")

                        if len(items) > 3:
                            item_descriptions.append('...')

                        ui.markdown(', '.join(item_descriptions)).classes('text-sm text-gray-600 mt-2')
                
                if IS_MOBILE():
                    ui.separator()

        load_orders()

@ui.page('/order/{order_id}')
def order_detail_page(order_id: str):
    navbar()

    if not IS_LOGGED_IN():
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-6 max-w-4xl mx-auto'):
        ui.label(f'Детали заказа #{order_id}').classes('text-3xl font-bold text-center mb-4')

        order = get_order_by_id(USER_AUTH_TOKEN(), order_id)
        if not order or "detail" in order:
            with ui.card().classes('w-full p-6 bg-red-50 text-red-600 rounded-lg text-center'):
                ui.label('Заказ не найден').classes('text-xl font-medium')
            return

        buyer_id = order.get('buyer_id')
        buyer_profile = None
        if buyer_id:
            try:
                buyer_profile = get_profile_by_id(USER_AUTH_TOKEN(), buyer_id)  # получаем профиль покупателя
            except Exception as e:
                buyer_profile = None
                print("Ошибка загрузки профиля покупателя:", e)

        with ui.card().classes('w-full p-6 rounded-xl bg-white' + (' shadow-lg' if not IS_MOBILE() else ' shadow-none')):
            with ui.row().classes('justify-between items-center w-full border-b pb-3 mb-4'):
                ui.label(f"Номер заказа: #{order['order_id']}").classes('text-lg font-semibold')
                ui.label(f"Дата: {order['order_date']}").classes('text-sm text-gray-500')
                ui.label('Закрыт' if order['is_closed'] else 'Открыт').classes('text-sm' + (' text-red-500' if order['is_closed'] else ' text-green-500'))

            if buyer_profile:
                with ui.link(target=f'/profile/{buyer_profile["id"]}').classes('font-semibold no-underline hover:underline text-primary'):
                    ui.label(f"Покупатель: {buyer_profile['display_name']}").classes('text-md')
            else:
                ui.label('Информация о покупателе недоступна').classes('text-sm text-red-500')

            ui.label('Товары в заказе:').classes('font-medium mt-2 mb-3')

            with ui.list().props('bordered separator').classes('w-full rounded-lg overflow-hidden'):
                for item in order['items']:
                    flower_data = get_flower_data(flower_id=item['flower_id'])
                    flower_name = flower_data[0]['name'] if isinstance(flower_data, list) else flower_data.get('name', 'Неизвестный товар')
                    
                    with ui.item().props('dense clickable').classes('hover:bg-blue-50 transition-colors items-center') as item_element:
                        with ui.link(target=f'/flower/{item["flower_id"]}').classes('w-full no-underline'):
                            ui.item_label(f"{flower_name} ×{item['quantity']}").classes('text-sm')

            with ui.row().classes('mt-6 justify-end w-full'):
                ui.button('Назад к списку заказов', on_click=lambda: ui.navigate.back()).props('outline color=primary').classes('px-4 py-2')
                
                if IS_USER_SELLER() or IS_USER_ADMIN():
                    def update_status(token: str, order_id: int):
                        try:
                            response = update_order_status(token, order_id)
                            if response.get('detail') == 'Данные заказа успешно обновлены':
                                ui.notify('Статус заказа успешно обновлен', color='green')
                                time.sleep(1)
                                ui.navigate.to(f"/order/{order['order_id']}")
                            else:
                                ui.notify('Ошибка при обновлении статуса заказа', color='red')
                        except Exception as e:
                            ui.notify(f'Ошибка: {str(e)}', color='red')

                    ui.button('Изменить статус заказа', on_click=lambda: update_status(USER_AUTH_TOKEN(), order['order_id'])).props('color=secondary').classes('px-4 py-2')
    