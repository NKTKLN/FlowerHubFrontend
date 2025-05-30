import pytest
from playwright.sync_api import Page, expect

@pytest.mark.describe("Register page tests")
class TestRegisterPage:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/register")

    @pytest.mark.it("should show error on invalid email")
    def test_invalid_email(self, page: Page):
        page.fill('input[type="email"]', 'invalid-email')
        page.fill('input[type="password"]', 'password123')
        page.fill('input[aria-label="Имя"]', 'Иван')
        page.fill('input[aria-label="Фамилия"]', 'Иванов')
        page.click('button:has-text("Зарегистрироваться")')
        expect(page.locator('.q-notification__message')).to_have_text("Введите корректный адрес электронной почты")

    @pytest.mark.it("should show error on short password")
    def test_short_password(self, page: Page):
        page.fill('input[type="email"]', 'user@example.com')
        page.fill('input[type="password"]', '123')
        page.fill('input[aria-label="Имя"]', 'Иван')
        page.fill('input[aria-label="Фамилия"]', 'Иванов')
        page.click('button:has-text("Зарегистрироваться")')
        expect(page.locator('.q-notification__message')).to_have_text("Пароль должен содержать не менее 6 символов")

    @pytest.mark.it("should show error when first name or last name is missing")
    def test_missing_name(self, page: Page):
        page.fill('input[type="email"]', 'user@example.com')
        page.fill('input[type="password"]', 'password123')
        page.fill('input[aria-label="Имя"]', '')
        page.fill('input[aria-label="Фамилия"]', '')
        page.click('button:has-text("Зарегистрироваться")')
        expect(page.locator('.q-notification__message')).to_have_text("Введите имя и фамилию")

    @pytest.mark.it("should register successfully and navigate to login")
    def test_successful_registration(self, page: Page):
        email = f"test123{page.context.new_page().context.storage_state().get('timestamp', '123')}@example.com"
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', email)
        page.fill('input[aria-label="Имя"]', 'Иван')
        page.fill('input[aria-label="Фамилия"]', 'Иванов')
        page.click('button:has-text("Зарегистрироваться")')
        page.wait_for_url("http://localhost:8080/login")

    @pytest.mark.it("should navigate to login page on link click")
    def test_navigate_to_login(self, page: Page):
        page.click('text=Уже есть аккаунт?')
        page.wait_for_url("http://localhost:8080/login")

    @pytest.mark.it("should navigate to home page on link click")
    def test_navigate_to_home(self, page: Page):
        page.click('text=Вернуться на главную')
        page.wait_for_url("http://localhost:8080/")
