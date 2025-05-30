from nicegui import app, ui
from app.services import seller_add_flower as seller_add_flower_api
from app.services import admin_add_flower as admin_add_flower_api
from app.services import reference as ref_api
from app.services import get_profile as get_profile_api
from app.services import get_flower_data, seller_edit_flower, get_admin_users, admin_add_user, admin_delete_user
from app.utils import USER_AUTH_TOKEN, IS_LOGGED_IN, IS_USER_SELLER, IS_USER_ADMIN  
from app.components import navbar, load_reference_data

@ui.page('/users')
def admin_users():
    navbar()

    if not IS_LOGGED_IN() or not  IS_USER_ADMIN():
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-6 max-w-4xl mx-auto'):
        ui.label('Пользователи').classes('text-2xl font-bold mb-4')

        create_user_table()

@ui.refreshable
def create_user_table():
    # Получаем список пользователей
    users = get_admin_users(USER_AUTH_TOKEN())

    # Определяем колонки таблицы
    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
        {'name': 'display_name', 'label': 'Имя', 'field': 'display_name', 'align': 'left', 'sortable': True},
        {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left', 'sortable': True},
        {'name': 'is_user_seller', 'label': 'Продавец', 'field': 'is_user_seller', 'align': 'center'},
        {'name': 'is_user_admin', 'label': 'Админ', 'field': 'is_user_admin', 'align': 'center'},
        {'name': 'actions', 'label': 'Действия', 'field': 'actions', 'align': 'right'}
    ]

    # Создаем таблицу
    table = ui.table(
        columns=columns,
        rows=users,
        row_key='id',
        pagination=10
    ).classes('w-full h-96 overflow-y-auto').props('bordered flat')

    # Добавляем действия (например, удаление или редактирование)
    table.add_slot('body-cell-actions', '''
        <q-td key="actions" :props="props">
            <q-btn 
                flat 
                dense 
                color="red" 
                label="Удалить" 
                @click="$parent.$emit('delete', props.row)" 
            />
        </q-td>
    ''')

    def handle_delete(event):
        user = event.args
        with ui.dialog() as dialog:
            with ui.card():
                ui.label(f"Вы уверены, что хотите удалить пользователя {user['display_name']}?")
                with ui.row().classes('justify-end mt-4 gap-2'):
                    ui.button('Отмена', on_click=dialog.close).props('outline')
                    ui.button('Удалить', on_click=lambda: [delete_user(user), dialog.close()]).props('color=red')
        dialog.open()

    table.on('delete', handle_delete)

    # Кнопка для добавления пользователя (если нужно)
    ui.button('Добавить пользователя', on_click=open_user_modal).classes('mt-4')


def delete_user(user):
    result = admin_delete_user(USER_AUTH_TOKEN(), user['id'])
    if result and "успешно" in result.get("detail", ""):
        ui.notify('Пользователь успешно удален!', color='green')
        create_user_table.refresh()
    else:
        ui.notify('Ошибка при удалении пользователя', color='red')


def open_user_modal():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-full max-w-md'):
        new_email = ui.input('Email').classes('w-full mb-4')
        new_first_name = ui.input('Имя').classes('w-full mb-4')
        new_last_name = ui.input('Фамилия').classes('w-full mb-4')
        new_display_name = ui.input('Отображаемое имя').classes('w-full mb-4')
        new_is_seller = ui.checkbox('Продавец')
        new_is_admin = ui.checkbox('Администратор')

        with ui.row().classes('justify-end mt-4 gap-2'):
            ui.button('Отмена', on_click=dialog.close).props('outline')
            ui.button('Добавить', on_click=lambda: save_user(
                new_email.value,
                new_first_name.value,
                new_last_name.value,
                new_display_name.value,
                new_is_seller.value,
                new_is_admin.value,
                dialog
            )).props('color=primary')
    dialog.open()


def save_user(email, first_name, last_name, display_name, is_seller, is_admin, dialog):
    if not email or not display_name:
        ui.notify('Email и Отображаемое имя обязательны', color='red')
        return

    payload = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": display_name,
        "is_user_seller": is_seller,
        "is_user_admin": is_admin
    }

    result = admin_add_user(USER_AUTH_TOKEN(), payload)
    if result and result.get("id"):
        dialog.close()
        ui.notify('Пользователь успешно добавлен!', color='green')
        create_user_table.refresh()
    else:
        ui.notify('Ошибка при добавлении пользователя', color='red')
