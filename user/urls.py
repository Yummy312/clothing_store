from django.urls import path
from .views import UserCreateView, UserFavoriteView,LoginView, LogoutView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('favorite/', UserFavoriteView.as_view(), name='user-favorite'),
    path('favorite/<int:pk>/', UserFavoriteView.as_view(), name='user-favorite-delete'),
]