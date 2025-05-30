import pytest
from playwright.sync_api import Page, expect

users = {
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
}

class TestFlowersPages:

    def login(self, page: Page, email: str, password: str):
        page.goto("http://localhost:8080/login")
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    def test_access_denied_for_unauthenticated_on_add(self, page: Page):
        page.goto("http://localhost:8080/flowers/add")
        expect(page).to_have_url("http://localhost:8080/")

    def test_access_denied_for_buyer_on_add(self, page: Page):
        self.login(page, users["buyer"]["email"], users["buyer"]["password"])
        page.goto("http://localhost:8080/flowers/add")
        expect(page).to_have_url("http://localhost:8080/")

    def test_access_allowed_for_seller_on_add(self, page: Page):
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto("http://localhost:8080/flowers/add")
        expect(page.locator('button.mt-4:has-text("Добавить цветок")')).to_be_visible()

    def test_access_allowed_for_admin_on_add(self, page: Page):
        self.login(page, users["admin"]["email"], users["admin"]["password"])
        page.goto("http://localhost:8080/flowers/add")
        expect(page.locator('button.mt-4:has-text("Добавить цветок")')).to_be_visible()
        expect(page.locator('input[aria-label="ID Поставщика"]')).to_be_visible()

    def test_edit_flower_access_denied_for_buyer(self, page: Page):
        flower_id = "1"
        self.login(page, users["buyer"]["email"], users["buyer"]["password"])
        page.goto(f"http://localhost:8080/flower/{flower_id}/edit")
        expect(page).to_have_url("http://localhost:8080/")

    def test_edit_flower_access_allowed_for_seller(self, page: Page):
        flower_id = "1"
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto(f"http://localhost:8080/flower/{flower_id}/edit")
        expect(page.locator("text=Редактировать цветок")).to_be_visible()
        expect(page.locator('input[aria-label="Название цветка"]')).to_be_visible()

    def test_edit_flower_save_changes(self, page: Page):
        flower_id = "1"
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto(f"http://localhost:8080/flower/{flower_id}/edit")

        new_name = "Тестовый цветок изменённый"
        page.fill('input[aria-label="Название цветка"]', new_name)
        page.click('button:has-text("Сохранить изменения")')

        # Проверяем появление уведомления об успехе
        expect(page.locator(f'text=Цветок успешно обновлён!')).to_be_visible()

    def test_cancel_button_navigates_back(self, page: Page):
        flower_id = "1"
        self.login(page, users["seller"]["email"], users["seller"]["password"])
        page.goto(f"http://localhost:8080/flower/{flower_id}/edit")

        page.click('button:has-text("Отмена")')
        expect(page).to_have_url(f"http://localhost:8080/flower/{flower_id}")

