from nicegui import ui
from app.components import load_reference_data
from app.services import reference as ref_api
from app.utils import USER_AUTH_TOKEN, IS_LOGGED_IN, IS_USER_SELLER, IS_USER_ADMIN
from app.components import navbar

@ui.page('/reference/list')
def reference_list():
    navbar()
    
    if not IS_LOGGED_IN() or not (IS_USER_SELLER() or IS_USER_ADMIN()):
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full p-6 gap-8 max-w-6xl mx-auto'):
        ui.label('Справочные данные').classes('text-3xl font-bold mb-2')

        create_reference_table(
            title='Типы цветов',
            data_fetcher=ref_api.get_types,
            columns=['ID', 'Name', 'Description'],
            row_key='id',
            add_button_text='Добавить тип',
            modal_handler=open_type_modal,
            delete_handler=delete_type
        )

        create_reference_table(
            title='Места посадки',
            data_fetcher=ref_api.get_usages,
            columns=['ID', 'Name', 'Description'],
            row_key='id',
            add_button_text='Добавить место посадки',
            modal_handler=open_usage_modal,
            delete_handler=delete_usage
        )

        create_reference_table(
            title='Сезоны цветения',
            data_fetcher=ref_api.get_seasons,
            columns=['ID', 'Name', 'Description'],
            row_key='id',
            add_button_text='Добавить сезон',
            modal_handler=open_season_modal,
            delete_handler=delete_season    
        )

        create_reference_table(
            title='Страны производства',
            data_fetcher=ref_api.get_countries,
            columns=['ID', 'Name', 'Code'],
            row_key='id',
            add_button_text='Добавить страну',
            modal_handler=open_country_modal,
            delete_handler=delete_country
        )

type_id, usage_id, season_id, country_id = load_reference_data()

@ui.refreshable
def create_reference_table(title, data_fetcher, columns, row_key, add_button_text, modal_handler, delete_handler):
    ui.label(title).classes('text-xl font-semibold')

    data = data_fetcher()
    table_columns = [
        {'name': col.lower().replace(' ', '_'), 'label': col, 'field': col.lower().replace(' ', '_'), 'align': 'left', 'sortable': True}
        for col in columns
    ]
    table_columns.append({
        'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'right'
    })

    table = ui.table(
        columns=table_columns,
        rows=data,
        row_key=row_key,
        pagination=10,
    ).classes('w-full h-80 overflow-y-auto').props('bordered flat')

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
        row = event.args
        with ui.dialog() as dialog:
            with ui.card():
                ui.label("Вы уверены, что хотите удалить эту запись?")
                with ui.row().classes('justify-end mt-4 gap-2'):
                    ui.button('Отмена', on_click=dialog.close).props('outline')
                    ui.button('Удалить', on_click=lambda: [delete_handler(row), dialog.close()]).props('color=red')
        dialog.open()

    table.on('delete', handle_delete)

    ui.button(add_button_text, on_click=modal_handler)

def delete_type(item):
    result = ref_api.delete_type(USER_AUTH_TOKEN(), item['id'])
    if result and "успешно" in result.get("detail"):
        ui.notify('Тип успешно удален!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при удалении типа', color='red')

def delete_usage(item):
    result = ref_api.delete_usage(USER_AUTH_TOKEN(), item['id'])
    if result and "успешно" in result.get("detail"):
        ui.notify('Место посадки успешно удалено!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при удалении места посадки', color='red')

def delete_season(item):
    result = ref_api.delete_season(USER_AUTH_TOKEN(), item['id'])
    if result and "успешно" in result.get("detail"):
        ui.notify('Сезон успешно удален!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при удалении сезона', color='red')

def delete_country(item):
    result = ref_api.delete_country(USER_AUTH_TOKEN(), item['id'])
    if result and "успешно" in result.get("detail"):
        ui.notify('Страна успешно удалена!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при удалении страны', color='red')

def open_type_modal():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-full max-w-md'):
        new_name = ui.input('Название типа').classes('w-full mb-4')
        new_desc = ui.textarea('Описание').props('rows=3').classes('w-full')
        with ui.row().classes('justify-end mt-4 gap-2'):
            ui.button('Отмена', on_click=dialog.close).props('outline')
            ui.button('Добавить', on_click=lambda: save_type(new_name.value, new_desc.value, dialog)).props('color=primary')
    dialog.open()

def save_type(name, desc, dialog):
    if not name:
        ui.notify('Введите название типа', color='red')
        return
    result = ref_api.add_type(USER_AUTH_TOKEN(), {'name': name, 'description': desc})
    if result and result.get('name') == name:
        dialog.close()
        ui.notify('Тип успешно добавлен!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при добавлении типа', color='red')

def open_usage_modal():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-full max-w-md'):
        new_name = ui.input('Название места посадки').classes('w-full mb-4')
        new_desc = ui.textarea('Описание').props('rows=3').classes('w-full')
        with ui.row().classes('justify-end mt-4 gap-2'):
            ui.button('Отмена', on_click=dialog.close).props('outline')
            ui.button('Добавить', on_click=lambda: save_usage(new_name.value, new_desc.value, dialog)).props('color=primary')
    dialog.open()

def save_usage(name, desc, dialog):
    if not name:
        ui.notify('Введите название места посадки', color='red')
        return
    result = ref_api.add_usage(USER_AUTH_TOKEN(), {'name': name, 'description': desc})
    if result and result.get('name') == name:
        dialog.close()
        ui.notify('Место посадки успешно добавлено!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при добавлении места посадки', color='red')

def open_season_modal():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-full max-w-md'):
        new_name = ui.input('Название сезона').classes('w-full mb-4')
        new_desc = ui.textarea('Описание').props('rows=3').classes('w-full')
        with ui.row().classes('justify-end mt-4 gap-2'):
            ui.button('Отмена', on_click=dialog.close).props('outline')
            ui.button('Добавить', on_click=lambda: save_season(new_name.value, new_desc.value, dialog)).props('color=primary')
    dialog.open()

def save_season(name, desc, dialog):
    if not name:
        ui.notify('Введите название сезона', color='red')
        return
    result = ref_api.add_season(USER_AUTH_TOKEN(), {'name': name, 'description': desc})
    if result and result.get('name') == name:
        dialog.close()
        ui.notify('Сезон успешно добавлен!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при добавлении сезона', color='red')

def open_country_modal():
    with ui.dialog() as dialog, ui.card().classes('p-4 w-full max-w-md'):
        new_name = ui.input('Название страны').classes('w-full mb-4')
        new_desc = ui.textarea('Код страны').props('rows=3').classes('w-full')
        with ui.row().classes('justify-end mt-4 gap-2'):
            ui.button('Отмена', on_click=dialog.close).props('outline')
            ui.button('Добавить', on_click=lambda: save_country(new_name.value, new_desc.value, dialog)).props('color=primary')
    dialog.open()

def save_country(name, desc, dialog):
    if not name:
        ui.notify('Введите название страны', color='red')
        return
    result = ref_api.add_country(USER_AUTH_TOKEN(), {'name': name, 'code': desc})
    if result and result.get('name') == name:
        dialog.close()
        ui.notify('Страна успешно добавлена!', color='green')
        create_reference_table.refresh()
    else:
        ui.notify('Ошибка при добавлении', color='red')[[2]]
