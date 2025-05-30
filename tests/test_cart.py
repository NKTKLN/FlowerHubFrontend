import pytest
from playwright.sync_api import Page, expect

users = {
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
}

@pytest.mark.describe("Cart page tests")
class TestCartPage:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/login")

    def login(self, page: Page, email: str, password: str):
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    @pytest.mark.it("unauthorized user should be redirected")
    def test_redirect_if_not_logged_in(self, page: Page):
        page.goto("http://localhost:8080/cart")
        expect(page).to_have_url("http://localhost:8080/")

    @pytest.mark.it("seller should be redirected from cart")
    def test_redirect_if_seller(self, page: Page):
        self.login(page, **users["seller"])
        page.goto("http://localhost:8080/cart")
        expect(page).to_have_url("http://localhost:8080/")

    @pytest.mark.it("empty cart should show appropriate message")
    def test_empty_cart_message(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/cart")
        expect(page.locator('text=Корзина пуста')).to_be_visible()
        expect(page.locator('text=Итого: 0 ₽')).to_be_visible()

    @pytest.mark.it("add and remove item from cart and check total")
    def test_add_remove_item(self, page: Page):
        self.login(page, **users["buyer"])

        page.goto("http://localhost:8080/")
        page.click('button.add-btn')

        page.goto("http://localhost:8080/cart")

        quantity_label = page.locator('text=1').first
        expect(quantity_label).to_be_visible()

        total_label = page.locator('text=Итого:').first
        expect(total_label).not_to_have_text('Итого: 0 ₽')

        page.click('button.add-btn')
        expect(page.locator('text=2').first).to_be_visible()

        page.click('button.delete-btn')
        expect(page.locator('text=1').first).to_be_visible()

    @pytest.mark.it("clear cart button should empty the cart")
    def test_clear_cart(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/")
        page.click('button.add-btn')
        page.goto("http://localhost:8080/cart")

        page.click('button:has-text("Очистить корзину")')
        expect(page.locator('text=Корзина пуста')).to_be_visible()

    @pytest.mark.it("place order should work and show success notification")
    def test_place_order(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/")
        page.click('button.add-btn')
        page.goto("http://localhost:8080/cart")

        page.click('button:has-text("Оформить заказ")')
        expect(page.locator('.q-notification__message')).to_have_text("Заказ успешно оформлен!")
