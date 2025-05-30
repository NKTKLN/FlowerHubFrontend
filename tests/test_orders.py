import re
import pytest
from playwright.sync_api import Page, expect

users = {
    "buyer": {"email": "test@test.ti", "password": "test@test.ti"},
    "no_order_buyer": {"email": "test@noorders.ti", "password": "test@noorders.ti"},
    "seller": {"email": "test@seller.ti", "password": "test@seller.ti"},
    "admin": {"email": "test@admin.ti", "password": "test@admin.ti"},
}

class TestOrdersPages:

    def login(self, page: Page, email: str, password: str):
        page.goto("http://localhost:8080/login")
        page.fill('input[type="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Войти")')
        page.wait_for_url("http://localhost:8080/")

    def test_orders_redirect_for_seller_or_not_logged(self, page: Page):
        page.goto("http://localhost:8080/orders")
        expect(page).to_have_url("http://localhost:8080/")

        self.login(page, **users["seller"])
        page.goto("http://localhost:8080/orders")
        expect(page).to_have_url("http://localhost:8080/")

    def test_orders_page_no_orders_message(self, page: Page):
        self.login(page, **users["no_order_buyer"])
        page.goto("http://localhost:8080/orders")

        expect(page.locator("text=Мои заказы")).to_be_visible()
        expect(page.locator("text=Нет оформленных заказов")).to_be_visible()

    def test_orders_page_show_orders(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/orders")

        expect(page.locator("text=Мои заказы")).to_be_visible()
        cards = page.locator('div.q-card')

        count = cards.count()
        assert count > 0, "Ожидалось больше 0 заказов на странице"

        expect(page.locator('text=Заказ #2')).to_be_visible()

    def test_seller_orders_redirect_for_non_seller(self, page: Page):
        page.goto("http://localhost:8080/seller/orders")
        expect(page).to_have_url("http://localhost:8080/")

        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/seller/orders")
        expect(page).to_have_url("http://localhost:8080/")

    def test_seller_orders_page_shows_orders(self, page: Page):
        self.login(page, **users["seller"])
        page.goto("http://localhost:8080/seller/orders")

        expect(page.locator('div.text-3xl.font-bold:has-text("Заказы пользователей")')).to_be_visible()
        cards = page.locator('div.q-card')

        count = cards.count()
        assert count > 0, "Ожидалось больше 0 заказов на странице"

    def test_order_detail_redirect_if_not_logged_in(self, page: Page):
        page.goto("http://localhost:8080/order/6")
        expect(page).to_have_url("http://localhost:8080/")

    def test_order_detail_shows_order_info(self, page: Page):
        self.login(page, **users["buyer"])
        order_id = "6"

        page.goto(f"http://localhost:8080/order/{order_id}")

        expect(page.locator(f"text=Детали заказа #{order_id}")).to_be_visible()
        expect(page.locator("text=Номер заказа:")).to_be_visible()
        expect(page.locator("text=Дата:")).to_be_visible()
        expect(page.locator("text=Покупатель:")).to_be_visible()
        expect(page.locator("text=Товары в заказе:")).to_be_visible()

    def test_order_detail_order_not_found(self, page: Page):
        self.login(page, **users["buyer"])
        page.goto("http://localhost:8080/order/nonexistent")
        expect(page.locator("text=Заказ не найден")).to_be_visible()
