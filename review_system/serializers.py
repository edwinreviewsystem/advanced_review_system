
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class ProductReviewsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(allow_null=True, required=False)
    class Meta:
        model = ProductReviews
        fields = ['id','star_rating', 'product_name', 'domain', 'name', 'email', 'review', 'image', 'source','created_at']
        
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
class ReviewFormDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFormDesign
        fields = ('generate_button', 'generate_button_text', 'button_color', 'button_text_color', 'label_text_color', 'background_color')

class ReviewListDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewListDesign
        fields = ('content_text_color', 'star_rating_color', 'reviewer_name_color', 'review_color')  

class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(allow_null=True, required=False)
    last_name = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Customer
        fields = '__all__'