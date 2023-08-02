import pytest
from django.contrib.auth import get_user_model
from product.models import Product
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


# Для создания нескольких товаров, а именно в кол-ве двух
@pytest.fixture
def create_products():
    products_to_create = [
        Product(name="T-shirt",
                description="A T-shirt is a lightweight and comfortable "
                            "shirt with short sleeves.",
                price=540),
        Product(name="jacket",
                description="Step out in confidence and elegance with"
                            " our stunning collection of jackets",

                price=740)
    ]
    products = Product.objects.bulk_create(products_to_create)

    return products


# Для создания одного товара
@pytest.fixture
def create_product():
    product = Product.objects.create(
        name="jeans",
        description="Jeans - trousers made of thick cotton"
                    " fabric with riveted seams on the pockets.",
        price=1250
    )
    return product


# Создаем тестовый клиент
@pytest.fixture
def api_client():
    return APIClient()


# Фикстура для создания суперпользователя
@pytest.fixture
def create_superuser():
    user_model = get_user_model()

    return user_model.objects.create_superuser(
        username='admin',
        email='admin@gmail.com',
        password='123',
    )


# Фикстура для создания пользователя
@pytest.fixture
def create_user():
    user_model = get_user_model()
    return user_model.objects.create_superuser(
        username='test',
        email='test@gmail.com',
        password='test4352',
    )
