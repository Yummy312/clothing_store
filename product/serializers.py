from rest_framework import serializers
from .models import Product
import string


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price")

    def validate_name(self, name):
        if any(char in name for char in string.punctuation):
            raise serializers.ValidationError("The name should not contain special characters.")

        if len(name) <= 1 :
            raise serializers.ValidationError("The name too short")
        return name

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError("The price should be a positive value.")
        return price
