import pytest
from urllib.parse import unquote
from playwright.sync_api import Page, expect

users = {
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
}

@pytest.mark.describe("Home page access and UI tests by roles")
class TestHomePageRoles:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/login")

    def login(self, page: Page, email: str, password: str):
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    @pytest.mark.it("buyer should see Add to cart buttons and not edit/delete")
    def test_buyer_ui(self, page: Page):
        self.login(page, **users["buyer"])

        add_buttons = page.locator('button.add-btn')
        assert add_buttons.count() > 0

        assert page.locator('button.edit-btn').count() == 0
        assert page.locator('button.delete-btn').count() == 0

    @pytest.mark.it("seller should see edit and delete buttons for their products")
    def test_seller_ui(self, page: Page):
        self.login(page, **users["seller"])

        assert page.locator('button.edit-btn').count() > 0
        assert page.locator('button.delete-btn').count() > 0
        assert page.locator('button.add-btn').count() == 0

    @pytest.mark.it("admin should see edit and delete buttons for all products")
    def test_admin_ui(self, page: Page):
        self.login(page, **users["admin"])

        assert page.locator('button.edit-btn').count() > 0
        assert page.locator('button.delete-btn').count() > 0
        assert page.locator('button.add-btn').count() == 0

    @pytest.mark.it("filters should apply and clear correctly")
    def test_filters(self, page: Page):
        self.login(page, **users["buyer"])

        page.fill('input[aria-label=Название]', "Роза")
        with page.expect_navigation():
            page.click('button:has-text("Применить фильтры")')
        
        assert "name=Роза" in unquote(page.url)

        page.click('button:has-text("Очистить фильтры")')
        assert page.url.rstrip('/') == "http://localhost:8080"

    @pytest.mark.it("pagination buttons should navigate")
    def test_pagination(self, page: Page):
        self.login(page, **users["buyer"])

        next_button = page.locator('button:has-text("Вперёд")')
        prev_button = page.locator('button:has-text("Назад")')
        expect(next_button).to_be_visible()
        expect(prev_button).to_be_visible()

        with page.expect_navigation():
            next_button.click()
        assert "offset=" in page.url and "offset=0" not in page.url

        with page.expect_navigation():
            prev_button.click()
        assert "offset=0" in page.url or "offset" not in page.url
