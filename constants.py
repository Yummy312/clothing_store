from enum import Enum


class API:
    PRODUCT_URL = "http://127.0.0.1:8000/products/"
    REGISTER_URL = "http://127.0.0.1:8000/register/"
    LOGIN_URL = "http://127.0.0.1:8000/login/"
    LOGOUT_URL = "http://127.0.0.1:8000/logout/"
    FAVORITE_URL = "http://127.0.0.1:8000/favorite/"


class ErrorMessages(Enum):
    WRONG_STATUS_CODE = "Received status code is not equal to expected"
