from nicegui import app, ui
from app.services import seller_add_flower as seller_add_flower_api
from app.services import reference, get_flower_data, create_order, get_cart
from app.utils import USER_AUTH_TOKEN, IS_LOGGED_IN, IS_USER_SELLER
from app.components import navbar, load_reference_data

@ui.page('/cart')
def cart_page():
    navbar()

    if not IS_LOGGED_IN() or IS_USER_SELLER():
        ui.navigate.to('/')
        return
    
    app.storage.user['cart'] = get_cart(USER_AUTH_TOKEN())
    if 'cart' not in app.storage.user:
        app.storage.user['cart'] = {}

    with ui.column().classes('w-full p-6 gap-6 max-w-7xl mx-auto'):
        ui.label('Корзина').classes('text-3xl font-bold mb-2')

        cart_container = ui.column().classes('w-full gap-4')
        total_price_label = ui.label('Итого: 0 ₽').classes('text-xl font-bold mt-4 text-primary')

        def update_cart_ui():
            cart = dict(app.storage.user.get('cart', {}))
            cart_container.clear()
            total_price = 0

            if not cart:
                with cart_container:
                    ui.label('Корзина пуста').classes('text-lg text-gray-500')
                total_price_label.set_text('Итого: 0 ₽')
                return

            flowers = []
            for flower_id_str, quantity in cart.items():
                try:
                    flower_id = int(flower_id_str)
                except ValueError:
                    continue

                result = get_flower_data(flower_id=flower_id)

                if isinstance(result, list) and len(result) > 0:
                    flower = result[0]
                elif isinstance(result, dict):
                    flower = result
                else:
                    continue

                flowers.append((flower, quantity))

            with cart_container:
                for flower, quantity in flowers:
                    price_total = flower['price'] * quantity
                    fid = flower['id']

                    with ui.card().classes('w-full flex sm:flex-row flex-col items-center gap-4 p-4 shadow-md'):
                        with ui.link(target=f'/flower/{flower["id"]}').classes('flex-1 no-underline cursor-pointer'):
                            ui.label(flower['name']).classes('text-lg text-black font-semibold')

                        with ui.row().classes('items-center gap-2 whitespace-nowrap'):
                            def on_minus(fid=fid):
                                cart = app.storage.user.get('cart', {})
                                current = cart.get(str(fid), 0)
                                if current > 0:
                                    cart[str(fid)] = current - 1
                                    if cart[str(fid)] == 0:
                                        del cart[str(fid)]
                                    app.storage.user['cart'] = cart
                                    update_cart_ui()

                            def on_plus(fid=fid):
                                cart = app.storage.user.get('cart', {})
                                current = cart.get(str(fid), 0)
                                cart[str(fid)] = current + 1
                                app.storage.user['cart'] = cart
                                update_cart_ui()

                            ui.button(icon="remove", on_click=on_minus).props('dense outline size=sm color=secondary').classes('delete-btn')
                            ui.label(str(quantity)).classes('min-w-[1.5rem] text-center')
                            ui.button(icon="add", on_click=on_plus).props('dense outline size=sm color=primary').classes('add-btn')
                            ui.label(f'{price_total} ₽').classes('font-medium min-w-[5rem] text-right')

                    total_price += price_total

            total_price_label.set_text(f'Итого: {total_price} ₽')

        def clear_cart():
            app.storage.user['cart'] = {}
            update_cart_ui()

        def place_order():
            cart = app.storage.user.get('cart', {})
            if not cart:
                ui.notify('Корзина пуста!', type='negative')
                return

            data = create_order(USER_AUTH_TOKEN(), cart)
            if data.get("details") == "Заказ оформлен успешно":
                clear_cart()
                ui.notify('Заказ успешно оформлен!', type='positive')
            else:
                ui.notify(data.get("details"), type='error')

        with ui.row().classes('w-full justify-end mt-4 gap-4'):
            ui.button('Очистить корзину', on_click=clear_cart).props('outline color=red')
            ui.button('Оформить заказ', icon='shopping_basket', on_click=place_order).props('color=primary')

        update_cart_ui()
