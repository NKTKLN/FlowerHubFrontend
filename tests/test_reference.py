import pytest
from playwright.sync_api import Page, expect

users = {
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
}

class TestReferenceList:

    def login(self, page: Page, email: str, password: str):
        page.goto("http://localhost:8080/login")
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    def test_access_for_seller(self, page: Page):
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto("http://localhost:8080/reference/list")
        expect(page.locator('div.mb-2:has-text("Справочные данные")')).to_be_visible()

        expect(page.get_by_text("Типы цветов")).to_be_visible()
        expect(page.get_by_text("Места посадки")).to_be_visible()
        expect(page.get_by_text("Сезоны цветения")).to_be_visible()
        expect(page.get_by_text("Страны производства")).to_be_visible()

        expect(page.get_by_role("button", name="Добавить тип")).to_be_visible()
        expect(page.get_by_role("button", name="Добавить место посадки")).to_be_visible()
        expect(page.get_by_role("button", name="Добавить сезон")).to_be_visible()
        expect(page.get_by_role("button", name="Добавить страну")).to_be_visible()

    def test_access_for_admin(self, page: Page):
        self.login(page, users["admin"]["email"], users["admin"]["password"])
        page.goto("http://localhost:8080/reference/list")
        expect(page.locator('div.mb-2:has-text("Справочные данные")')).to_be_visible()

    def test_access_denied_for_buyer(self, page: Page):
        self.login(page, users["buyer"]["email"], users["buyer"]["password"])
        page.goto("http://localhost:8080/reference/list")
        expect(page).to_have_url("http://localhost:8080/")

    def test_open_add_type_modal(self, page: Page):
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto("http://localhost:8080/reference/list")

        page.get_by_role("button", name="Добавить тип").click()
        dialog = page.locator(".q-dialog__inner")
        expect(dialog.locator("text=Название типа")).to_be_visible()

    def test_delete_confirmation_dialog(self, page: Page):
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto("http://localhost:8080/reference/list")
        delete_buttons = page.locator('button', has_text='Удалить')
        if delete_buttons.count() > 0:
            delete_buttons.first.click()
            expect(page.get_by_text("Вы уверены, что хотите удалить эту запись?")).to_be_visible()
