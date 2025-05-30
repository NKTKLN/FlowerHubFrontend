from nicegui import ui
from app.services import reference as ref_api


def load_reference_data(
    initial_type=None,
    initial_usage=None,
    initial_season=None,
    initial_country=None
):
    types = ref_api.get_types()
    usages = ref_api.get_usages()
    seasons = ref_api.get_seasons()
    countries = ref_api.get_countries()

    type_options = {t['id']: t['name'] for t in types}
    usage_options = {u['id']: u['name'] for u in usages}
    season_options = {s['id']: s['name'] for s in seasons}
    country_options = {c['id']: c['name'] for c in countries}

    # Устанавливаем значение по умолчанию или из параметра
    type_value = initial_type if initial_type in type_options else (types[0]['id'] if types else None)
    usage_value = initial_usage if initial_usage in usage_options else (usages[0]['id'] if usages else None)
    season_value = initial_season if initial_season in season_options else (seasons[0]['id'] if seasons else None)
    country_value = initial_country if initial_country in country_options else (countries[0]['id'] if countries else None)

    type_id = ui.select(
        label='Тип',
        options=type_options,
        value=type_value
    ).classes('w-full mb-4')

    usage_id = ui.select(
        label='Где сажать',
        options=usage_options,
        value=usage_value
    ).classes('w-full mb-4')

    season_id = ui.select(
        label='Сезон цветения',
        options=season_options,
        value=season_value
    ).classes('w-full mb-4')

    country_id = ui.select(
        label='Страна произрастания',
        options=country_options,
        value=country_value
    ).classes('w-full mb-4')

    return type_id, usage_id, season_id, country_id
