import pytest
from playwright.sync_api import Page, expect

users = {
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
    "no_order_buyer": {"email": "test@noorders.ti", "password": "test@noorders.ti"},
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
}

class TestAdminUsersPage:

    def login(self, page: Page, email: str, password: str):
        page.goto("http://localhost:8080/login")
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    def test_redirect_if_not_logged_in(self, page: Page):
        page.goto("http://localhost:8080/users")
        expect(page).to_have_url("http://localhost:8080/")

    def test_redirect_if_not_admin(self, page: Page):
        self.login(page, users["buyer"]["email"], users["buyer"]["password"])
        page.goto("http://localhost:8080/users")
        expect(page).to_have_url("http://localhost:8080/")

    def test_users_page_shows_table(self, page: Page):
        self.login(page, users["admin"]["email"], users["admin"]["password"])
        page.goto("http://localhost:8080/users")

        expect(page.locator("text=Пользователи")).to_be_visible()
        expect(page.locator("table")).to_be_visible()
        expect(page.locator("text=ID")).to_be_visible()
        expect(page.locator("text=Имя")).to_be_visible()
        expect(page.locator("text=Email")).to_be_visible()

    def test_open_add_user_modal(self, page: Page):
        self.login(page, users["admin"]["email"], users["admin"]["password"])
        page.goto("http://localhost:8080/users")

        add_button = page.locator('button:has-text("Добавить пользователя")')
        add_button.click()

        expect(page.locator('input[aria-label="Email"]')).to_be_visible()
        expect(page.locator('input[aria-label="Имя"]')).to_be_visible()
        expect(page.locator('input[aria-label="Фамилия"]')).to_be_visible()
        expect(page.locator('input[aria-label="Отображаемое имя"]')).to_be_visible()
        expect(page.locator('.q-checkbox__label:has-text("Продавец")')).to_be_visible()
        expect(page.locator('.q-checkbox__label:has-text("Администратор")')).to_be_visible()

    def test_add_user_validation(self, page: Page):
        self.login(page, users["admin"]["email"], users["admin"]["password"])
        page.goto("http://localhost:8080/users")
        page.locator('button:has-text("Добавить пользователя")').click()
        dialog_locator = page.locator('div[role="dialog"]')
        add_button = dialog_locator.locator('button:has-text("Добавить")')
        add_button.click()
        expect(page.locator('text=Email и Отображаемое имя обязательны')).to_be_visible()

    def test_delete_user_dialog_opens(self, page: Page):
        self.login(page, users["admin"]["email"], users["admin"]["password"])
        page.goto("http://localhost:8080/users")

        delete_buttons = page.locator('button:has-text("Удалить")')
        if delete_buttons.count() > 0:
            delete_buttons.first.click()
            expect(page.locator('text=Вы уверены, что хотите удалить пользователя')).to_be_visible()
        else:
            pytest.skip("Нет пользователей для удаления")
