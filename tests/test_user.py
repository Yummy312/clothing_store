import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from product.models import Product
from tests.conftest import api_client, create_product, create_product, create_products
from rest_framework import status
from constants import API
from django.urls import reverse


@pytest.mark.django_db
def test_register_view_user(api_client):
    # Создаем модель User
    user_model = get_user_model()

    url = "http://127.0.0.1:8000/register/"
    data = {"email": "qwerty@gmail.com", "username": "qwerty",
            "password": "simplepassword123"}

    # Отправляем запрос на создание пользователя
    response = api_client.post(API.REGISTER_URL, data, format="json")

    # Проверяем, что статус равен 201(т.е создано)
    assert response.status_code == status.HTTP_201_CREATED

    # Проверяем, действительно ли у нас создался данный пользователь
    assert user_model.objects.filter(email=data["email"]).exists()


@pytest.mark.django_db
def test_register_view_user_wrong_data(api_client):
    user_model = get_user_model()

    # Неверные данные: поле username не является списком
    data = {
        "email": "roomate@gmail.com", "username": [],
        "password": "fedora321"
    }
    # Отправляем POST-запрос на тестовый сервер
    response = api_client.post(API.REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Неверные данные: поле password имеет слишком короткий пароль
    data = {
        "email": "roomate@gmail.com", "username": "room",
        "password": "222"
    }
    # Отправляем POST-запрос на тестовый сервер
    response = api_client.post(API.REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Неверные данные: поле email имеет неправильный формат(т.е пропущен символ @)
    data = {
        "email": "roomategmail.com", "username": "room",
        "password": "222"
    }
    # Отправляем POST-запрос на тестовый сервер
    response = api_client.post(API.REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_view_valid_credentials(api_client):
    # Создаем пользователя в БД
    user = get_user_model().objects.create_user(username="test",
                                                email="test@gmail.com",
                                                password="test4356")

    # Отправляем POST-запрос на тестовый сервер для логина
    data = {"email": "test@gmail.com", "password": "test4356"}
    response = api_client.post(API.LOGIN_URL, data, format="json")

    # Проверяем статус код ответа - ожидаем 200 (Успех) для успешного логина
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что в ответе есть ключ 'token'
    assert 'token' in response.data

    # Получаем токен пользователя из базы данных
    token = Token.objects.get(user=user)

    # Проверяем, что токен в ответе совпадает с токеном пользователя
    assert response.data['token'] == token.key


@pytest.mark.django_db
def test_login_view_user_not_found(api_client):
    # Отправляем запрос на тестовый сервер с email, который не существует
    data = {"email": "vergo@gmail.com", "password": "11sjs1123"}
    response = api_client.post(API.LOGIN_URL, data, format="json")

    # Проверяем статус кода 401(неверный запрос)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Проверяем, что в ответе есть ключ 'error'
    assert 'error' in response.data


@pytest.mark.django_db
def test_login_view_invalid_credentials(api_client):
    # Создаем пользователя в БД
    user = get_user_model().objects.create_user(username="test",
                                                email="test@gmail.com",
                                                password="test4356")
    # Отправляем запрос с неправильным паролем
    data = {"email": "test@gmail.com", "password": "test1111"}
    response = api_client.post(API.LOGIN_URL, data, format="json")

    # Проверяем статус кода 401(ожидаем - что не авторизован)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_view_user(api_client):
    # Создаем пользователя в БД
    user = get_user_model().objects.create_user(username="mark",
                                                email="mark@gmail.com",
                                                password="kivo3321")
    # Получаем токен
    token = Token.objects.get_or_create(user=user)

    # Теперь отправляем запрос, чтобы выйти из учетной записи
    api_client.force_authenticate(token=token, user=user)
    response = api_client.post(API.LOGOUT_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logout_view_invalid_token(api_client):
    # Создаем неcуществующий токен
    wrong_token = "Token sadsi122dskdcx31zsdd"

    # Отправляем запрос
    api_client.credentials(HTTP_AUTHORIZATION=wrong_token)
    response = api_client.post(API.LOGOUT_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data


@pytest.mark.django_db
def test_favorite_view_get_list_products(api_client, create_user, create_products):
    # Создаем пользователя в БД
    user = create_user

    # Создаем товары в БД в количестве двух экземпляров
    products = create_products

    # Добавляем товары в Избранное
    user.favorites.add(products[0])
    user.favorites.add(products[1])

    # Получаем токен
    token = Token.objects.get_or_create(user=user)[0]

    # Устанавливаем соединение
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # Отправляем запрос на тестовый сервер, чтобы получить товары из Избранных
    response = api_client.get(API.FAVORITE_URL)

    # Верные данные(Ожидаем статус 200)
    assert response.status_code == status.HTTP_200_OK

    # Проверяем кол-во избранных товаров
    assert len(response.data) == 2


@pytest.mark.django_db
def test_favorite_view_add_product_to_favorite(api_client, create_product, create_user):
    # Создаем товар в БД чтобы в дальнейшем можно было добавить его в Избранное
    product = create_product

    # Создаем пользователя в БД
    user = create_user

    # Получаем токен
    token = Token.objects.get_or_create(user=user)[0]

    # Устанавливаем соединение
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # Отправляем запрос на тестовый сервер, чтобы добавить товар по его id в Избранное
    data = {"product_id": 1}
    response = api_client.post(API.FAVORITE_URL, data, format="json")

    # Проверяем статус код 201(ожидаем что товар будет добавлен в Избранное)
    assert response.status_code == status.HTTP_201_CREATED

    # Проверяем что действительно товар был добавлен в Избранное
    assert user.favorites.filter(id=data["product_id"]).exists()

    # Неверные данные: несуществующий id товара
    data = {"product_id": 6251}
    response = api_client.post(API.FAVORITE_URL, data, format="json")

    # Ожидаем статус 404(Т.е товар не найден)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data

    # Неверные данные: пустой запрос
    response = api_client.post(API.FAVORITE_URL, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Неверные данные: поле 'product_id' не является строкой
    response = api_client.post(API.FAVORITE_URL, {"product_id": "ss"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_favorite_view_delete_product_from_favorite(api_client, create_product, create_user):
    # Создаем товар в БД
    product = create_product
    # Создаем эндпоинт для удаления товара из Избранных

    # Создаем пользователя
    user = create_user

    # Получаем токен
    token = Token.objects.get_or_create(user=user)[0]

    # Добавляем товар в Избранное
    user.favorites.add(product)

    # Устанавливаем соединение
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # Получаем id cуществующего товара
    id_exists_product = str(create_product.id) + '/'

    # Удаляем товар из Избранных
    response = api_client.delete(API.FAVORITE_URL + id_exists_product)

    # Ожидаем код 204(т.е контент удален)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Неверные данные: несуществующий id товара
    response = api_client.delete(API.FAVORITE_URL + '2434' + '/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
