import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from users.models import Role
from products.models import Product


@pytest.fixture
def roles(db):
    admin_role = Role.objects.create(name="admin")
    client_role = Role.objects.create(name="client")
    return {"admin": admin_role, "client": client_role}


@pytest.fixture
def admin_user(db, roles):
    user_model = get_user_model()
    user = user_model.objects.create_user(  # type: ignore[arg-type]
        email="admin@example.com",
        password="adminpass123",
        role=roles["admin"],
        is_staff=True,
    )
    return user


@pytest.fixture
def client_user(db, roles):
    user_model = get_user_model()
    user = user_model.objects.create_user(  # type: ignore[arg-type]
        email="client@example.com",
        password="clientpass123",
        role=roles["client"],
    )
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestProductPermissions:
    create_payload = {
        "name": "Monitor",
        "description": "Monitor 24 pulgadas",
        "price": "1200.00",
        "stock": 15,
    }

    def test_admin_can_create_product(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)

        response = api_client.post("/api/products/", self.create_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name=self.create_payload["name"]).exists()

    def test_non_admin_cannot_create_product(self, api_client, client_user):
        api_client.force_authenticate(user=client_user)

        response = api_client.post("/api/products/", self.create_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Product.objects.filter(name=self.create_payload["name"]).exists()

    def test_admin_can_update_product(self, api_client, admin_user):
        product = Product.objects.create(  # type: ignore[misc]
            name="Laptop",
            description="Equipo portátil",
            price="2000.00",
            stock=10,
        )

        api_client.force_authenticate(user=admin_user)

        response = api_client.patch(
            f"/api/products/{product.pk}/",
            {"price": "2500.00"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert str(product.price) == "2500.00"

    def test_non_admin_cannot_update_product(self, api_client, client_user):
        product = Product.objects.create(  # type: ignore[misc]
            name="Mouse",
            description="Dispositivo inalámbrico",
            price="100.00",
            stock=30,
        )

        api_client.force_authenticate(user=client_user)

        response = api_client.patch(
            f"/api/products/{product.pk}/",
            {"price": "150.00"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        product.refresh_from_db()
        assert str(product.price) == "100.00"
