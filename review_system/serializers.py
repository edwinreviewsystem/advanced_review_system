from rest_framework import serializers
from .models import ProductReviews
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class ProductReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviews
        fields = ['id','star_rating', 'name', 'email', 'product_id', 'review', 'image', 'created_at']
        
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        return value