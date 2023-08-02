from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        # Открываем доступ только суперпользователю для создания товара
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
