from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from .models import User
from product.models import Product
from product.serializers import ProductSerializer
from rest_framework.authtoken.models import Token
from .serializers import UserCreateSerializer, UserFavoriteCreateSerializers
from rest_framework import mixins
from rest_framework import status


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserFavoriteView(generics.GenericAPIView,
                       mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserFavoriteCreateSerializers

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound("User not found.")

    def get_product(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("product not found")

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = user.favorites.all()
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        email = request.user.email
        user = self.get_user(email)
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data.get("product_id")
        product = self.get_product(product_id)
        user.favorites.add(product)
        user.save()
        return Response(status=201)

    def delete(self, request, pk, *args, **kwargs):
        email = request.user.email
        user = self.get_user(email)
        # Проверяем есть ли у пользователя в Избранных тот товар, который он хочет удалить
        if user.favorites.filter(id=pk).exists():
            product = self.get_product(pk)
            user.favorites.remove(product)
            user.save()
            return Response(status=204)
        else:
            raise NotFound("product not found from favorites")

