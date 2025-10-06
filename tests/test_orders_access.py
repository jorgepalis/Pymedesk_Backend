import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from users.models import Role
from products.models import Product
from orders.models import Order, OrderItem


@pytest.fixture
def roles(db):
    admin_role = Role.objects.create(name="admin")
    client_role = Role.objects.create(name="client")
    return {"admin": admin_role, "client": client_role}


@pytest.fixture
def admin_user(db, roles):
    user_model = get_user_model()
    email = "admin@example.com"
    return user_model.objects.create_user(  # type: ignore[arg-type]
        email=email,
        password="adminpass123",
        role=roles["admin"],
        is_staff=True,
    )


@pytest.fixture
def client_user_a(db, roles):
    user_model = get_user_model()
    email = "client_a@example.com"
    return user_model.objects.create_user(  # type: ignore[arg-type]
        email=email,
        password="clientpass123",
        role=roles["client"],
    )


@pytest.fixture
def client_user_b(db, roles):
    user_model = get_user_model()
    email = "client_b@example.com"
    return user_model.objects.create_user(  # type: ignore[arg-type]
        email=email,
        password="clientpass123",
        role=roles["client"],
    )


@pytest.fixture
def sample_products(db):
    product = Product.objects.create(
        name="Teclado",
        description="Teclado mecánico",
        price="300.00",
        stock=50,
    )
    return product


@pytest.fixture
def orders(db, sample_products, client_user_a, client_user_b):
    order_a = Order.objects.create(user=client_user_a, total_price="300.00")
    order_b = Order.objects.create(user=client_user_b, total_price="300.00")

    OrderItem.objects.create(
        order=order_a,
        product=sample_products,
        quantity=1,
        subtotal="300.00",
    )
    OrderItem.objects.create(
        order=order_b,
        product=sample_products,
        quantity=1,
        subtotal="300.00",
    )
    return order_a, order_b


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestOrderAccessPermissions:
    endpoint = "/api/orders/"

    def test_client_sees_only_own_orders(self, api_client, client_user_a, orders):
        api_client.force_authenticate(user=client_user_a)

        response = api_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["user"]["id"] == client_user_a.id

    def test_admin_sees_all_orders(self, api_client, admin_user, orders):
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        user_ids = {item["user"]["id"] for item in data}
        assert user_ids == {orders[0].user.id, orders[1].user.id}
