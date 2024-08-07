from rest_framework import serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import User


class AIReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIReview
        fields = [ 'star_rating', 'product_name', 'review_tone' , 'user_selected_words']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password",'first_name','last_name','email')

        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        User.objects.all(), "A user with email already exists."
                    )
                ],
            },
        }

    def create(self, validated_data):
        username= validated_data.get("username")
        password = validated_data.get("password")
        first_name= validated_data.get("first_name")
        last_name= validated_data.get("last_name")
        email=validated_data.get("email")

        user = User.objects.create_user(username=username, password=password, first_name=first_name,last_name=last_name,email=email)
        return user


