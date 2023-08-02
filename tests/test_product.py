import pytest
from django.urls import reverse
from constants import API, ErrorMessages
from product.models import Product
from tests.conftest import api_client, create_products, create_product
from tests.conftest import create_superuser
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
def test_get_product_list_view(api_client, create_products):
    """
    Cначала мы проверяем статус, а потом проверяем данные. Потому, что, смысл
    нам делать более трудозатратные операции если у нас статус уже изначально например
    равен 400 или 500?
    """
    # Из класса API получаем URL
    url = API.PRODUCT_URL  # API.PRODUCT_URL == http://127.0.0.1:8000/products

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, ErrorMessages.WRONG_STATUS_CODE
    assert len(response.data) == 2


@pytest.mark.django_db
def test_get_product_view(create_product, api_client):
    # Используем reverse для получения URL представления деталей продукта
    url = reverse('product-detail', kwargs={'pk': create_product.pk})

    # Отправляем GET-запрос к представлению
    response = api_client.get(url)

    # Проверяем, что код ответа равен 200 OK (или другой ожидаемый код)
    assert response.status_code == status.HTTP_200_OK
    # Проверяем на соответствие полей
    assert response.data['name'] == create_product.name
    assert response.data['description'] == create_product.description


@pytest.mark.django_db
# Создаем коллекцию несуществующих id
@pytest.mark.parametrize('test_value', [1232, 2245])
def test_get_product_view_non_existent_id(create_product, test_value, api_client):
    url = reverse('product-detail', kwargs={'pk': test_value})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, ErrorMessages.WRONG_STATUS_CODE


@pytest.mark.django_db
def test_create_product_view(api_client, create_superuser):
    # Создаем пользователя и получаем его токен аутентификации так как наш апи требует токен при POST-запросе
    token, _ = Token.objects.get_or_create(user=create_superuser)
    superuser = create_superuser

    # Объявляем данные, которые нужны для создания товара
    data = {"name": "shirt", "description": "this is shirt", "price": 1236}
    # Забираем апи
    url = API.PRODUCT_URL

    # Устанавливаем аутентификацию с токеном в запросе
    api_client.force_authenticate(user=superuser, token=token)

    # Создаем запрос с помощью APIClient
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Product.objects.filter(name=data["name"]).exists()


@pytest.mark.django_db
def test_create_product_view_wrong_data(create_superuser):
    # Создаем пользователя и получаем его токен
    token, _ = Token.objects.get_or_create(user=create_superuser)
    superuser = create_superuser
    # Создаем клиента API
    client = APIClient()

    # Устанавливаем аутентификацию для клиента
    client.force_authenticate(user=superuser, token=token)

    url = API.PRODUCT_URL

    # Неверные данные: отсутствие поля 'name'
    data = {"description": "this is shirt", "price": 1236}
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Неверные данные: поле 'name' с пустым значением
    data = {"name": "", "description": "this is shirt", "price": 1236}
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Неверные данные: поле 'price' не является числом
    data = {"name": "shirt", "description": "this is shirt", "price": "not_a_number"}
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_product_view_anonymous_user():
    # Создаем тестового анонимного клиента
    client = APIClient()

    # Пытаемся отправить запрос будучи не авторизованным
    url = API.PRODUCT_URL
    data = {"name": "boots", "description": "something", "price": 321}
    response = client.post(url, data, format="json")

    # Проверяем, что код ответа равен 401 (или другой ожидаемый код)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
