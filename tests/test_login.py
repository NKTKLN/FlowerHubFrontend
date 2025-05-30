import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("Login page tests")
class TestLoginPage:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/login")

    @pytest.mark.it("should show validation error on invalid email")
    def test_invalid_email(self, page: Page):
        page.fill('input[type="email"]', 'invalid-email')
        page.fill('input[type="password"]', 'password123')
        page.click('button:has-text("Войти")')
        expect(page.locator('.q-notification__message')).to_have_text("Введите корректный адрес электронной почты")

    @pytest.mark.it("should navigate to home on successful login")
    def test_successful_login(self, page: Page, monkeypatch):
        page.fill('input[type="email"]', 'test@test.ti')
        page.fill('input[type="password"]', 'test@test.ti')
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    @pytest.mark.it("should show error notification on failed login")
    def test_failed_login(self, page: Page):
        page.fill('input[type="email"]', 'user@example.com')
        page.fill('input[type="password"]', 'wrong_password')
        page.click('button:has-text("Войти")')
        expect(page.locator('.q-notification__message')).to_have_text("Incorrect username or password")

    @pytest.mark.it("should navigate to register page when clicking on 'Нет аккаунта?'")
    def test_navigate_to_register(self, page: Page):
        page.click('text=Нет аккаунта?')
        page.wait_for_url("http://localhost:8080/register")

    @pytest.mark.it("should navigate to home page when clicking on 'Вернуться на главную'")
    def test_navigate_to_home(self, page: Page):
        page.click('text=Вернуться на главную')
        page.wait_for_url("http://localhost:8080/")
