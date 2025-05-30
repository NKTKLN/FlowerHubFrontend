import pytest
import re
from playwright.sync_api import Page, expect

users = {
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
}

class TestUserProfile:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/login")

    def login(self, page: Page, email: str, password: str):
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    def get_logged_user_id(self, page: Page) -> str:
        page.goto("http://localhost:8080/profile")
        page.wait_for_url(re.compile(r'/profile/\d+'))
        return page.url.split("/")[-1]

    def test_redirect_if_not_logged_in_profile_edit(self, page: Page):
        page.goto("http://localhost:8080/profile/edit")
        expect(page).to_have_url("http://localhost:8080/")

    def test_profile_page_shows_user_info(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/profile")
        expect(page).to_have_url(re.compile(r"/profile/\d+"))
        expect(page.locator("text=Основная информация")).to_be_visible()
        expect(page.locator("text=Покупатель")).to_be_visible()

    def test_edit_profile_validation_email(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/profile/edit")

        email_input = page.get_by_label("Почта")
        email_input.fill("not-an-email")
        page.get_by_text("Сохранить изменения").click()

        expect(page.locator(".q-notification__message")).to_have_text("Введите корректный адрес электронной почты")

    def test_change_password_success_and_error(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/profile/edit")

        # too short
        page.get_by_label("Новый пароль", exact=True).fill("123")
        page.get_by_label("Подтвердите новый пароль", exact=True).fill("123")
        page.get_by_text("Сменить пароль").click()
        expect(page.get_by_text("Новый пароль должен содержать не менее 6 символов", exact=True)).to_be_visible()

        # mismatch
        page.get_by_label("Новый пароль", exact=True).fill("1234567")
        page.get_by_label("Подтвердите новый пароль", exact=True).fill("7654321")
        page.get_by_text("Сменить пароль").click()
        expect(page.get_by_text("Новые пароли не совпадают", exact=True)).to_be_visible()

        # success (предполагаем, что пароль "123456" валиден)
        page.get_by_label("Новый пароль", exact=True).fill("test@test.ti")
        page.get_by_label("Подтвердите новый пароль", exact=True).fill("test@test.ti")
        page.get_by_text("Сменить пароль").click()
        expect(page.get_by_text("Пароль успешно изменён!", exact=True)).to_be_visible()

    def test_public_user_profile_view(self, page: Page):
        self.login(page, **users["buyer"])
        user_id = self.get_logged_user_id(page)

        page.goto(f"http://localhost:8080/profile/{user_id}")
        expect(page.locator("text=Основная информация")).to_be_visible()
        expect(page.locator("text=Редактировать профиль")).to_be_visible()
        expect(page.locator("text=Имя")).to_be_visible()
        expect(page.locator("text=Адрес")).to_be_visible()

    def test_seller_profile_shows_button_to_view_products(self, page: Page):
        self.login(page, **users["seller"])
        user_id = self.get_logged_user_id(page)

        page.goto(f"http://localhost:8080/profile/{user_id}")
        expect(page.locator("text=Посмотреть товары")).to_be_visible()
