from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User
import string


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_password(self, password):
        if len(password) < 8:
            raise ValidationError("The maximum password length must not be less than 8 characters ")
        if password.isalpha() or password.isdigit():
            raise serializers.ValidationError("Password must contain both letters and numbers.")
        return password

    def validate_username(self, username):
        # Custom validation for the 'name' field
        if len(username) <=1:
            raise ValidationError("The maximum password length must not be less than 8 characters ")
        if any(char in username for char in string.punctuation):
            raise serializers.ValidationError("The username should not contain special characters.")
        return username


class UserFavoriteCreateSerializers(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        request = self.context.get('request')
        if not request:
            raise ValidationError("Context does not contain 'request'.")

        user = request.user

        if not value:
            raise serializers.ValidationError("This field is required.")

        if user.favorites.filter(id=value).exists():
            raise serializers.ValidationError("Product already in favorites.")

        return value
